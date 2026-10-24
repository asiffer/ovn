"""MCP server exposing basic OVN Northbound operations."""

from collections.abc import Mapping
from typing import Any

from mcp.server import MCPServer

from ovn.models import (
    LogicalRouter,
    LogicalRouterPort,
    LogicalSwitch,
    LogicalSwitchPort,
)
from ovn.models.base import Model

mcp = MCPServer("ovn")


def _json_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted(_json_value(item) for item in value)
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def _dump_model(model: Model) -> dict[str, Any]:
    """Return the model's fields in a JSON-compatible form."""
    return {
        field: _json_value(getattr(model, field))
        for field in model.fields
        if hasattr(model, field)
    }


def _list_ports(owner: LogicalRouter | LogicalSwitch, port_model: type[Model]) -> list[dict[str, Any]]:
    port_ids = getattr(owner, "ports", set())
    return [
        _dump_model(port)
        for port in port_model.objects.list()
        if getattr(port, "_uuid", None) in port_ids
    ]


def _delete_model(model: type[Model], uuid: str) -> bool:
    instance = model.objects.get(uuid)
    if instance is None:
        return False
    instance.delete()
    return True


@mcp.tool()
def list_logical_switches() -> list[dict[str, Any]]:
    """List logical switches in the OVN Northbound database."""
    return [_dump_model(switch) for switch in LogicalSwitch.objects.list()]


@mcp.tool()
def get_logical_switch(name: str) -> dict[str, Any] | None:
    """Find a logical switch by its name."""
    switch = LogicalSwitch.objects.get_by_name(name)
    return None if switch is None else _dump_model(switch)


@mcp.tool()
def create_logical_switch(name: str) -> dict[str, Any]:
    """Create a logical switch with the given name."""
    return _dump_model(LogicalSwitch.objects.create(name=name))


@mcp.tool()
def delete_logical_switch(uuid: str) -> bool:
    """Delete a logical switch by its UUID."""
    return _delete_model(LogicalSwitch, uuid)


@mcp.tool()
def list_logical_routers() -> list[dict[str, Any]]:
    """List logical routers in the OVN Northbound database."""
    return [_dump_model(router) for router in LogicalRouter.objects.list()]


@mcp.tool()
def get_logical_router(name: str) -> dict[str, Any] | None:
    """Find a logical router by its name."""
    router = LogicalRouter.objects.get_by_name(name)
    return None if router is None else _dump_model(router)


@mcp.tool()
def create_logical_router(name: str) -> dict[str, Any]:
    """Create a logical router with the given name."""
    return _dump_model(LogicalRouter.objects.create(name=name))


@mcp.tool()
def delete_logical_router(uuid: str) -> bool:
    """Delete a logical router by its UUID."""
    return _delete_model(LogicalRouter, uuid)


@mcp.tool()
def list_logical_switch_ports(switch_uuid: str) -> list[dict[str, Any]]:
    """List ports attached to a logical switch."""
    switch = LogicalSwitch.objects.get(switch_uuid)
    if switch is None:
        raise ValueError(f"Logical switch {switch_uuid!r} not found")
    return _list_ports(switch, LogicalSwitchPort)


@mcp.tool()
def create_logical_switch_port(
    switch_uuid: str, name: str, addresses: list[str] | None = None
) -> dict[str, Any]:
    """Create a port attached to a logical switch."""
    switch = LogicalSwitch.objects.get(switch_uuid)
    if switch is None:
        raise ValueError(f"Logical switch {switch_uuid!r} not found")
    port = switch.create_port(name=name, addresses=set(addresses or []))
    return _dump_model(port)


@mcp.tool()
def delete_logical_switch_port(uuid: str) -> bool:
    """Delete a logical switch port by its UUID."""
    return _delete_model(LogicalSwitchPort, uuid)


@mcp.tool()
def list_logical_router_ports(router_uuid: str) -> list[dict[str, Any]]:
    """List ports attached to a logical router."""
    router = LogicalRouter.objects.get(router_uuid)
    if router is None:
        raise ValueError(f"Logical router {router_uuid!r} not found")
    return _list_ports(router, LogicalRouterPort)


@mcp.tool()
def create_logical_router_port(
    router_uuid: str, name: str, mac: str, networks: list[str]
) -> dict[str, Any]:
    """Create a port attached to a logical router."""
    router = LogicalRouter.objects.get(router_uuid)
    if router is None:
        raise ValueError(f"Logical router {router_uuid!r} not found")
    port = router.create_port(name=name, mac=mac, networks=set(networks))
    return _dump_model(port)


@mcp.tool()
def delete_logical_router_port(uuid: str) -> bool:
    """Delete a logical router port by its UUID."""
    return _delete_model(LogicalRouterPort, uuid)


def main() -> None:
    """Run the OVN MCP server over stdio."""
    mcp.run(transport="stdio")
