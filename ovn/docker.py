"""OVN Docker network plugin (libnetwork remote driver).

This turns ``ovn`` into a first-class Docker network driver: once it is running,
networks created with ``docker network create -d ovn ...`` are backed by OVN
logical switches, and every container attached to such a network gets a
``Logical_Switch_Port`` bound to the local integration bridge (``br-int``).

It implements Docker's `libnetwork remote driver protocol
<https://github.com/moby/moby/blob/master/libnetwork/docs/remote.md>`_: a small
FastAPI app served by uvicorn over a Unix socket under ``/run/docker/plugins/``.
Docker discovers the driver from the socket *filename* (``ovn.sock`` ->
driver ``ovn``) and drives it through a handful of ``POST`` endpoints.

Mapping to OVN (single host, ``Scope: local``):

==========================  ====================================================
libnetwork call             OVN / dataplane action
==========================  ====================================================
``CreateNetwork``           create a ``Logical_Switch`` named after the network
``DeleteNetwork``           delete that ``Logical_Switch``
``CreateEndpoint``          create a ``Logical_Switch_Port`` with the MAC/IP that
                            libnetwork's IPAM assigned (logical only, no veth yet)
``Join``                    create a ``veth`` pair, plug the host end into
                            ``br-int`` with ``external_ids:iface-id`` = endpoint
                            id, hand the container end to libnetwork to move into
                            the sandbox
``Leave``                   remove the OVS port and host veth
``DeleteEndpoint``          delete the ``Logical_Switch_Port``
==========================  ====================================================

``ovn-controller`` watches ``br-int``: when it sees an interface whose
``iface-id`` matches a ``Logical_Switch_Port`` name it binds the port and
programs the flows, so containers on the same network talk over local OpenFlow
forwarding (no tunnels on a single host).

The driver is **stateless**: everything it needs to answer a later call is kept
in OVN (switch/port rows, ``external_ids``) or derived deterministically from the
network/endpoint ids, so it survives a restart with no local database.

Requirements on the host:

- a working local OVS (``ovs-vswitchd`` + conf.db) with ``ovn-controller``
  running and ``br-int`` present (see ``docker/run.sh``),
- run as root (CAP_NET_ADMIN). The dataplane is pure Python -- no subprocesses:
  veths are created over netlink via ``pyroute2``, and the ``br-int`` port is
  written straight to the local Open vSwitch DB over OVSDB (no ``ip`` /
  ``ovs-vsctl``),
- the OVN NB DB reachable (``OVN_NB_DB``), e.g. ``tcp:127.0.0.1:6641``, and the
  local OVS DB reachable (``OVS_DB``, default ``unix:/var/run/openvswitch/db.sock``).

Run it (config via env vars or the matching CLI flags, flags winning; see
``ovn.settings.DriverSettings`` and ``python -m ovn.docker --help``)::

    sudo OVN_NB_DB=tcp:127.0.0.1:6641 python -m ovn.docker
    # or: sudo python -m ovn.docker --bridge br-int --ovs-db unix:/run/openvswitch/db.sock

then, from anywhere on the host::

    docker network create -d ovn --subnet 10.0.0.0/24 sw0
    docker run --rm -it --network sw0 alpine
"""

from __future__ import annotations

import argparse
import logging
import os
import random
from functools import lru_cache
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from pyroute2 import IPRoute
from starlette.datastructures import MutableHeaders

from ovn.client import OperationComposer
from ovn.models import LogicalSwitch, LogicalSwitchPort
from ovn.ovsdb import OVSDBClient
from ovn.settings import DriverSettings

logger = logging.getLogger("ovn.docker")

# Runtime configuration: env vars (see ovn.settings.DriverSettings) overridable
# by CLI flags. ``main`` applies the resolved values to this object once, before
# any request is served, so the handlers below read it live.
settings = DriverSettings()

# The Open vSwitch DB *name* is fixed by the OVS schema, not configurable.
OVS_DB_NAME = "Open_vSwitch"


def random_mac() -> str:
    """Return a locally-administered, unicast MAC address.

    Bit 0 (multicast) cleared, bit 1 (locally administered) set in the first
    octet so it never collides with a real vendor OUI.
    """
    first = (random.randint(0x00, 0xFF) & 0xFE) | 0x02
    rest = [random.randint(0x00, 0xFF) for _ in range(5)]
    return ":".join(f"{b:02x}" for b in [first, *rest])


# --- local OVS DB (OVSDB straight to the switch, no ovs-vsctl) --------------
#
# Plugging a veth into br-int is a write to the local Open vSwitch DB: insert an
# Interface and a Port, then add the Port to ``Bridge.ports``. We do that with
# the project's own OVSDB client pointed at the OVS socket -- the same wire
# protocol ovs-vsctl speaks, just in-process.


@lru_cache(maxsize=1)
def _ovs() -> OVSDBClient:
    """OVSDB client for the local Open vSwitch DB (distinct from the OVN NB DB)."""
    return OVSDBClient(settings.ovs_db)


def _ovs_map(pairs: dict[str, str]) -> list:
    """OVSDB-encode a string->string map column value."""
    return ["map", [[k, v] for k, v in pairs.items()]]


def _ovs_find_port(name: str) -> list | None:
    """Return the raw ``_uuid`` (``["uuid", ...]``) of Port ``name``, or None."""
    result = _ovs().transact(
        OVS_DB_NAME,
        OperationComposer()
        .select("Port", where=[("name", "==", name)], columns=["_uuid"])
        .operations(),
    )
    rows = result[0].get("rows") or []
    return rows[0]["_uuid"] if rows else None


def _ovs_add_port(bridge: str, name: str, external_ids: dict[str, str]) -> None:
    """Plug ``name`` into ``bridge`` with the given interface ``external_ids``.

    One transaction: insert the Interface and Port, then link the Port into
    ``Bridge.ports`` -- the equivalent of ``ovs-vsctl --may-exist add-port``.
    """
    if _ovs_find_port(name) is not None:  # --may-exist
        return
    composer = OperationComposer()
    composer.insert(
        "Interface",
        {"name": name, "external_ids": _ovs_map(external_ids)},
        uuid_name="iface",
    )
    composer.insert(
        "Port",
        {"name": name, "interfaces": ["set", [["named-uuid", "iface"]]]},
        uuid_name="port",
    )
    composer.mutate(
        "Bridge",
        where=[("name", "==", bridge)],
        mutations=[("ports", "insert", ["set", [["named-uuid", "port"]]])],
    )
    _ovs().transact(OVS_DB_NAME, composer.operations())


def _ovs_del_port(bridge: str, name: str) -> None:
    """Remove Port ``name`` from ``bridge`` if present.

    Detaching it from ``Bridge.ports`` is enough: OVSDB garbage-collects the now
    unreferenced Port and Interface rows (same effect as ``ovs-vsctl del-port``).
    """
    port_uuid = _ovs_find_port(name)
    if port_uuid is None:
        return
    _ovs().transact(
        OVS_DB_NAME,
        OperationComposer()
        .mutate(
            "Bridge",
            where=[("name", "==", bridge)],
            mutations=[("ports", "delete", ["set", [port_uuid]])],
        )
        .operations(),
    )


# --- veth dataplane (netlink via pyroute2, no ``ip`` subprocess) ------------


def _create_veth(host_veth: str, cont_veth: str, mac: str | None) -> None:
    """Create the veth pair, set the container end's MAC, bring the host end up.

    Rolls the pair back if any step fails, so a half-built pair never lingers.
    """
    with IPRoute() as ipr:
        ipr.link("add", ifname=cont_veth, kind="veth", peer=host_veth)
        try:
            (cont_idx,) = ipr.link_lookup(ifname=cont_veth)
            (host_idx,) = ipr.link_lookup(ifname=host_veth)
            if mac:
                ipr.link("set", index=cont_idx, address=mac)
            ipr.link("set", index=host_idx, state="up")
        except Exception:
            ipr.link("del", index=ipr.link_lookup(ifname=cont_veth)[0])
            raise


def _delete_veth(name: str) -> None:
    """Delete a link by name if present (removes both ends of the pair)."""
    with IPRoute() as ipr:
        for idx in ipr.link_lookup(ifname=name):
            ipr.link("del", index=idx)


# --- naming -----------------------------------------------------------------
#
# Linux interface names are capped at 15 chars (IFNAMSIZ - 1). The endpoint id
# is a long hex string, so the veth names are a deterministic prefix of it -- no
# local bookkeeping needed to recover them on Leave/DeleteEndpoint.


def _host_veth(endpoint_id: str) -> str:
    """Host-side veth name (plugged into ``br-int``)."""
    return endpoint_id[:15]


def _container_veth(endpoint_id: str) -> str:
    """Container-side veth name (moved into the sandbox by libnetwork)."""
    return endpoint_id[:13] + "_c"


def _lsp_mac(port: LogicalSwitchPort) -> str | None:
    """Pull the MAC out of a logical switch port's ``addresses`` (``"MAC IP"``)."""
    for entry in getattr(port, "addresses", None) or set():
        head = entry.split()[0] if entry.split() else ""
        if head and head not in ("router", "unknown", "dynamic"):
            return head
    return None


# --- request / response schemas --------------------------------------------
#
# libnetwork speaks JSON with capitalised field names; these Pydantic models
# mirror that exactly (so they serialise straight back) and ignore any extra
# fields a given Docker version might add.


class _Schema(BaseModel):
    model_config = ConfigDict(extra="ignore")


class IPAMData(_Schema):
    Pool: str = ""
    Gateway: str = ""


class EndpointInterface(_Schema):
    Address: str = ""
    AddressIPv6: str = ""
    MacAddress: str = ""


class ActivateResponse(_Schema):
    Implements: list[str]


class CapabilitiesResponse(_Schema):
    Scope: str
    ConnectivityScope: str


class CreateNetworkRequest(_Schema):
    NetworkID: str
    IPv4Data: list[IPAMData] = []
    Options: dict[str, Any] = {}


class DeleteNetworkRequest(_Schema):
    NetworkID: str


class CreateEndpointRequest(_Schema):
    NetworkID: str
    EndpointID: str
    Interface: EndpointInterface = EndpointInterface()


class CreateEndpointResponse(_Schema):
    Interface: EndpointInterface


class EndpointRequest(_Schema):
    """Shared shape of Join / Leave / DeleteEndpoint / EndpointOperInfo."""

    NetworkID: str = ""
    EndpointID: str
    SandboxKey: str = ""


class InterfaceName(_Schema):
    SrcName: str
    DstPrefix: str = "eth"


class JoinResponse(_Schema):
    InterfaceName: InterfaceName
    Gateway: str = ""
    GatewayIPv6: str = ""


class EndpointInfoResponse(_Schema):
    Value: dict[str, str] = {}


# --- app & error handling ---------------------------------------------------
#
# The protocol reports failures as ``{"Err": "..."}`` with a 200 status (not an
# HTTP error code). Handlers raise ``DriverError`` for expected/logical failures
# and let anything else bubble up; both -- plus request-validation errors -- are
# turned into that shape by the exception handlers below, which keeps every
# endpoint free to declare a single typed success response.


class DriverError(Exception):
    """Logical failure reported to libnetwork as ``{"Err": ...}``."""


app = FastAPI(title="OVN Docker network plugin")


@app.middleware("http")
async def _normalize_content_type(request: Request, call_next):
    """Make libnetwork's JSON bodies parseable by FastAPI.

    Docker's libnetwork does not reliably tag plugin request bodies as
    ``application/json`` (it may send a vendor ``*+json`` type, ``text/plain``,
    or no Content-Type at all). FastAPI only decodes a body into a typed model
    when the Content-Type is JSON-ish; otherwise it hands Pydantic the raw
    bytes, which fail validation. This plugin only ever receives JSON bodies,
    so force ``application/json`` on every request before routing — empty-body
    calls (handshake / no-ops) are unaffected since FastAPI skips parsing them.
    """
    headers = MutableHeaders(scope=request.scope)
    original_ct = headers.get("content-type")
    if original_ct != "application/json":
        headers["content-type"] = "application/json"
    return await call_next(request)


@app.exception_handler(DriverError)
async def _on_driver_error(request: Request, exc: DriverError) -> JSONResponse:
    logger.warning("%s: %s", request.url.path, exc)
    return JSONResponse({"Err": str(exc)}, status_code=200)


@app.exception_handler(RequestValidationError)
async def _on_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse({"Err": f"invalid request: {exc.errors()}"}, status_code=200)


@app.exception_handler(Exception)
async def _on_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("%s failed", request.url.path)
    return JSONResponse({"Err": str(exc)}, status_code=200)


# --- handshake --------------------------------------------------------------


@app.post("/Plugin.Activate")
def activate() -> ActivateResponse:
    return ActivateResponse(Implements=["NetworkDriver"])


@app.post("/NetworkDriver.GetCapabilities")
def get_capabilities() -> CapabilitiesResponse:
    # Single host: the switch and its bindings are local to this chassis.
    return CapabilitiesResponse(Scope="local", ConnectivityScope="global")


# --- networks ---------------------------------------------------------------


@app.post("/NetworkDriver.CreateNetwork")
def create_network(req: CreateNetworkRequest) -> dict:
    external_ids = {"docker-network": req.NetworkID}
    if req.IPv4Data:
        subnet = req.IPv4Data[0].Pool
        gateway = req.IPv4Data[0].Gateway.rsplit("/", 1)[0]
        if subnet:
            external_ids["subnet"] = subnet
        if gateway:
            external_ids["gateway"] = gateway

    if LogicalSwitch.objects.get_by_name(req.NetworkID) is None:
        LogicalSwitch.objects.create(name=req.NetworkID, external_ids=external_ids)
        logger.info("created logical switch for network %s", req.NetworkID)
    return {}


@app.post("/NetworkDriver.DeleteNetwork")
def delete_network(req: DeleteNetworkRequest) -> dict:
    sw = LogicalSwitch.objects.get_by_name(req.NetworkID)
    if sw is not None:
        LogicalSwitch.objects.delete(sw._uuid)
        logger.info("deleted logical switch for network %s", req.NetworkID)
    return {}


# --- endpoints --------------------------------------------------------------


@app.post("/NetworkDriver.CreateEndpoint")
def create_endpoint(req: CreateEndpointRequest) -> CreateEndpointResponse:
    sw = LogicalSwitch.objects.get_by_name(req.NetworkID)
    if sw is None:
        raise DriverError(f"create_endpoint: unknown network {req.NetworkID}")

    address = req.Interface.Address.rsplit("/", 1)[0]
    # Honour libnetwork's MAC if it set one; otherwise pick one and echo it back.
    requested_mac = req.Interface.MacAddress
    mac = requested_mac or random_mac()

    lsp_address = f"{mac} {address}" if address else mac
    sw.create_port(
        name=req.EndpointID,
        addresses={lsp_address},
        port_security={lsp_address},
        external_ids={
            "docker-network": req.NetworkID,
            "docker-endpoint": req.EndpointID,
        },
    )
    logger.info("created logical switch port %s on %s", req.EndpointID, req.NetworkID)

    return CreateEndpointResponse(
        Interface=EndpointInterface(MacAddress="" if requested_mac else mac)
    )


@app.post("/NetworkDriver.DeleteEndpoint")
def delete_endpoint(req: EndpointRequest) -> dict:
    port = LogicalSwitchPort.objects.get_by_name(req.EndpointID)
    if port is not None:
        LogicalSwitchPort.objects.delete(port._uuid)
        logger.info("deleted logical switch port %s", req.EndpointID)
    return {}


@app.post("/NetworkDriver.EndpointOperInfo")
def endpoint_oper_info(req: EndpointRequest) -> EndpointInfoResponse:
    port = LogicalSwitchPort.objects.get_by_name(req.EndpointID)
    if port is None:
        return EndpointInfoResponse()
    return EndpointInfoResponse(
        Value={
            "iface-id": req.EndpointID,
            "host-veth": _host_veth(req.EndpointID),
            "mac": _lsp_mac(port) or "",
        }
    )


@app.post("/NetworkDriver.Join")
def join(req: EndpointRequest) -> JoinResponse:
    port = LogicalSwitchPort.objects.get_by_name(req.EndpointID)
    if port is None:
        raise DriverError(f"join: unknown endpoint {req.EndpointID}")
    mac = _lsp_mac(port)

    host_veth = _host_veth(req.EndpointID)
    cont_veth = _container_veth(req.EndpointID)
    # SandboxKey is /var/run/docker/netns/<id>; its basename identifies the box.
    vm_id = req.SandboxKey.rsplit("/", 1)[-1]

    # The container end (cont_veth) is what libnetwork moves into the sandbox;
    # the host end (host_veth) stays here, plugged into br-int.
    _create_veth(host_veth, cont_veth, mac)
    try:
        _ovs_add_port(
            settings.bridge,
            host_veth,
            {
                "iface-id": req.EndpointID,
                "attached-mac": mac or "",
                "vm-id": vm_id,
                "iface-status": "active",
            },
        )
    except Exception:
        # Best-effort rollback so a failed join leaves no half-wired veth.
        _ovs_del_port(settings.bridge, host_veth)
        _delete_veth(cont_veth)
        raise

    sw = LogicalSwitch.objects.get_by_name(req.NetworkID)
    gateway = ""
    if sw is not None:
        gateway = (getattr(sw, "external_ids", None) or {}).get("gateway", "")

    logger.info(
        "joined endpoint %s (veth %s <-> %s)", req.EndpointID, host_veth, cont_veth
    )
    return JoinResponse(
        InterfaceName=InterfaceName(SrcName=cont_veth, DstPrefix="eth"),
        Gateway=gateway,
    )


@app.post("/NetworkDriver.Leave")
def leave(req: EndpointRequest) -> dict:
    host_veth = _host_veth(req.EndpointID)
    _ovs_del_port(settings.bridge, host_veth)
    # Deleting either side of the pair removes both; the container end is gone
    # with the sandbox, so target the host end.
    _delete_veth(host_veth)
    logger.info("left endpoint %s", req.EndpointID)
    return {}


# Optional calls we acknowledge but don't act on. They take no body parameter,
# so any (or no) payload Docker sends is simply ignored.
@app.post("/NetworkDriver.DiscoverNew")
@app.post("/NetworkDriver.DiscoverDelete")
@app.post("/NetworkDriver.ProgramExternalConnectivity")
@app.post("/NetworkDriver.RevokeExternalConnectivity")
def _noop() -> dict:
    return {}


# --- server -----------------------------------------------------------------


def _socket_path(addr: str) -> str:
    """Filesystem path of the Unix socket to listen on.

    Accepts ``unix:/path`` (the canonical form) or a bare ``/path``.
    """
    return addr.removeprefix("unix:")


def serve(socket: str | None = None) -> None:
    """Run the plugin server on a Unix socket until interrupted.

    ``socket`` defaults to ``settings.socket`` (``unix:/path`` or a bare path).
    Docker discovers the driver from the socket *filename* (``ovn.sock`` ->
    driver ``ovn``), so no plugin spec file is needed.
    """
    import uvicorn

    path = _socket_path(socket or settings.socket)
    logger.info(
        "OVN docker network plugin starting on %s (bridge=%s, ovs_db=%s)",
        path,
        settings.bridge,
        settings.ovs_db,
    )

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    if os.path.exists(path):
        os.unlink(path)
    try:
        uvicorn.run(app, uds=path, log_level="info")
    finally:
        if os.path.exists(path):
            os.unlink(path)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="OVN Docker network plugin")
    parser.add_argument(
        "--socket",
        default=settings.socket,
        help="Unix socket to listen on [env: OVN_PLUGIN_SOCKET] "
        f"(default: {settings.socket})",
    )
    parser.add_argument(
        "--bridge",
        default=settings.bridge,
        help=f"OVN integration bridge [env: OVN_BRIDGE] (default: {settings.bridge})",
    )
    parser.add_argument(
        "--ovs-db",
        dest="ovs_db",
        default=settings.ovs_db,
        help=f"local Open vSwitch OVSDB socket [env: OVS_DB] (default: {settings.ovs_db})",
    )
    parser.add_argument(
        "--log-level", default="INFO", help="logging level (default: INFO)"
    )
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # CLI flags win over env/defaults; apply them before serving so the handlers
    # (which read ``settings`` live) see the final configuration.
    settings.socket = args.socket
    settings.bridge = args.bridge
    settings.ovs_db = args.ovs_db
    serve(args.socket)


if __name__ == "__main__":
    main()
