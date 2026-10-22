"""High-level helpers for common OVN Northbound networking workflows.

These helpers compose the regular ORM models; they do not replace the
lower-level model API. Multi-row workflows use several ORM operations and are
not atomic, so a database error can leave earlier rows in place.
"""

import ipaddress
from dataclasses import dataclass
from typing import Iterable, Literal, Mapping, Sequence

from ovn.models import (
    ACL,
    DHCPOptions,
    LoadBalancer,
    LogicalRouter,
    LogicalRouterPort,
    LogicalSwitch,
    LogicalSwitchPort,
    NAT,
    PortGroup,
)


@dataclass
class NetworkSegment:
    """A routed logical switch and its router-facing port."""

    switch: LogicalSwitch
    switch_router_port: LogicalSwitchPort
    router_port: LogicalRouterPort
    dhcp_options: DHCPOptions | None = None


@dataclass
class TenantNetwork:
    """An isolated logical router with one routed network segment."""

    router: LogicalRouter
    segment: NetworkSegment


@dataclass(frozen=True)
class ACLRule:
    """A single OVN ACL rule to attach to a port group."""

    match: str
    direction: Literal["from-lport", "to-lport"] = "to-lport"
    priority: int = 1001
    action: Literal[
        "allow", "allow-related", "allow-stateless", "drop", "pass", "reject"
    ] = "allow-related"
    name: str | None = None


def create_network_segment(
    *,
    name: str,
    subnet: str,
    gateway: str,
    router: LogicalRouter,
    router_port_mac: str,
    dhcp_options: Mapping[str, str] | None = None,
) -> NetworkSegment:
    """Create a switch, connect it to a router, and optionally enable DHCP.

    ``dhcp_options`` supplies OVN DHCP option key/value pairs. When provided,
    the resulting DHCP options row is returned for use with
    :func:`attach_workload`.
    """
    network = ipaddress.ip_network(subnet, strict=False)
    gateway_address = ipaddress.ip_address(gateway)
    if gateway_address.version != network.version or gateway_address not in network:
        raise ValueError(f"Gateway {gateway!r} must be inside subnet {subnet!r}")

    switch = LogicalSwitch(name=name, other_config={"subnet": str(network)})
    switch.save()

    router_port = router.create_port(
        name=f"{name}-router",
        mac=router_port_mac,
        networks={f"{gateway_address}/{network.prefixlen}"},
    )
    switch_router_port = switch.create_port(name=f"{name}-router")
    switch_router_port.plug(router_port)

    dhcp = None
    if dhcp_options is not None:
        dhcp = DHCPOptions(cidr=str(network), options=dict(dhcp_options))
        dhcp.save()

    return NetworkSegment(
        switch=switch,
        switch_router_port=switch_router_port,
        router_port=router_port,
        dhcp_options=dhcp,
    )


def attach_workload(
    switch: LogicalSwitch,
    *,
    name: str,
    mac: str,
    ip_address: str | None = None,
    dhcp_options: DHCPOptions | None = None,
    port_security: bool = True,
) -> LogicalSwitchPort:
    """Attach a static or DHCP-addressed workload port to a logical switch."""
    if (ip_address is None) == (dhcp_options is None):
        raise ValueError("Provide exactly one of ip_address or dhcp_options")

    if dhcp_options is not None:
        address = "dynamic"
        row = {
            "addresses": {address},
            "dhcpv4_options": dhcp_options._uuid,
            "port_security": {mac} if port_security else set(),
        }
    else:
        address = f"{mac} {ip_address}"
        row = {
            "addresses": {address},
            "port_security": {address} if port_security else set(),
        }
    return switch.create_port(name=name, **row)


def create_tenant_network(
    *,
    name: str,
    subnet: str,
    gateway: str,
    router_port_mac: str,
    dhcp_options: Mapping[str, str] | None = None,
) -> TenantNetwork:
    """Create a tenant router and a single routed switch segment."""
    router = LogicalRouter(name=f"{name}-router")
    router.save()
    segment = create_network_segment(
        name=name,
        subnet=subnet,
        gateway=gateway,
        router=router,
        router_port_mac=router_port_mac,
        dhcp_options=dhcp_options,
    )
    return TenantNetwork(router=router, segment=segment)


def configure_outbound_nat(
    router: LogicalRouter,
    *,
    logical_ip: str,
    external_ip: str,
    gateway_port: LogicalRouterPort | None = None,
) -> NAT:
    """Add a source-NAT rule for a private subnet to a router.

    This creates the NAT rule only; it does not configure an external network,
    router interface, or default route.
    """
    network = ipaddress.ip_network(logical_ip, strict=False)
    external_address = ipaddress.ip_address(external_ip)
    if network.version != external_address.version:
        raise ValueError("logical_ip and external_ip must use the same IP version")

    nat = NAT(
        type="snat",
        logical_ip=str(network),
        external_ip=str(external_address),
    )
    if gateway_port is not None:
        nat.gateway_port = gateway_port._uuid
    nat.save()

    router_nat = set(getattr(router, "nat", set()) or set())
    router_nat.add(nat._uuid)
    router.nat = router_nat
    router.save()
    return nat


def apply_security_policy(
    port_group: PortGroup,
    rules: Iterable[ACLRule],
) -> list[ACL]:
    """Create ACL rows from ``rules`` and attach them to a port group."""
    rule_list = list(rules)
    if not rule_list:
        raise ValueError("At least one ACL rule is required")

    acls = []
    for rule in rule_list:
        acl = ACL(
            name=rule.name,
            direction=rule.direction,
            priority=rule.priority,
            action=rule.action,
            match=rule.match,
        )
        acl.save()
        acls.append(acl)

    group_acls = set(getattr(port_group, "acls", set()) or set())
    group_acls.update(acl._uuid for acl in acls)
    port_group.acls = group_acls
    port_group.save()
    return acls


def allow_web_traffic(
    port_group: PortGroup,
    *,
    direction: Literal["from-lport", "to-lport"] = "to-lport",
    priority: int = 1001,
) -> list[ACL]:
    """Allow TCP traffic to HTTP and HTTPS ports for a port group."""
    return apply_security_policy(
        port_group,
        (
            ACLRule(
                match=f"ip && tcp && tcp.dst == {port}",
                direction=direction,
                priority=priority,
                action="allow-related",
                name=f"allow-tcp-{port}",
            )
            for port in (80, 443)
        ),
    )


def create_service_endpoint(
    *,
    name: str,
    vip: str,
    backends: Sequence[str],
    switches: Sequence[LogicalSwitch] = (),
    routers: Sequence[LogicalRouter] = (),
    protocol: Literal["tcp", "udp", "sctp"] = "tcp",
) -> LoadBalancer:
    """Create a load-balancer VIP and attach it to switches and/or routers.

    ``vip`` and each backend use OVN's ``IP:port`` representation.
    """
    if not backends:
        raise ValueError("At least one load-balancer backend is required")

    load_balancer = LoadBalancer(
        name=name,
        protocol=protocol,
        vips={vip: ",".join(backends)},
    )
    load_balancer.save()

    for resource in (*switches, *routers):
        attached = set(getattr(resource, "load_balancer", set()) or set())
        attached.add(load_balancer._uuid)
        resource.load_balancer = attached
        resource.save()

    return load_balancer


__all__ = [
    "ACLRule",
    "NetworkSegment",
    "TenantNetwork",
    "allow_web_traffic",
    "apply_security_policy",
    "attach_workload",
    "configure_outbound_nat",
    "create_network_segment",
    "create_service_endpoint",
    "create_tenant_network",
]
