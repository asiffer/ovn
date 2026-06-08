from typing import TYPE_CHECKING, Tuple

from ovn.models._columns import LogicalSwitchColumns
from ovn.models.base import Model
from ovn.models.logical_switch_port import LogicalSwitchPort

if TYPE_CHECKING:
    from ovn.models.logical_router import LogicalRouter
    from ovn.models.logical_router_port import LogicalRouterPort


class LogicalSwitch(LogicalSwitchColumns, Model):
    def create_port(self, **kwargs) -> LogicalSwitchPort:
        """Create a logical switch port attached to this switch"""
        return LogicalSwitchPort.objects.add_to_logical_switch(self, **kwargs)

    def plug(
        self, device: "LogicalRouter", **kwargs
    ) -> Tuple[LogicalSwitchPort, "LogicalRouterPort"]:
        """Connect this switch to a logical router.

        Creates the matching switch and router ports and wires them together.
        Extra kwargs (``mac``, ``networks``, ...) are forwarded to the router
        port.
        """
        from ovn.models.logical_router import LogicalRouter

        if not isinstance(device, LogicalRouter):
            raise TypeError(f"Cannot plug a switch to {type(device).__name__}")

        switch_port = self.create_port(name=f"{self.name}_port{len(self.ports)}")
        router_port = device.create_port(
            name=f"{device.name}_port{len(device.ports)}", **kwargs
        )
        switch_port.plug(router_port)
        return switch_port, router_port
