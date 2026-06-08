from typing import TYPE_CHECKING

from ovn.manager import Manager
from ovn.models._columns import LogicalSwitchPortColumns
from ovn.models.base import Model

if TYPE_CHECKING:
    from ovn.models.logical_router_port import LogicalRouterPort
    from ovn.models.logical_switch import LogicalSwitch


class LogicalSwitchPortManager(Manager):
    def add_to_logical_switch(
        self, switch: "LogicalSwitch", **kwargs
    ) -> "LogicalSwitchPort":
        """Bind the port to a logical switch"""
        raw, _ = self.client.create_and_bind(
            table_create=self._table,
            row_create=kwargs,
            table_bind=switch._table(),
            attr_bind="ports",
            where_bind=[("_uuid", "==", ("uuid", switch._uuid))],
        )
        return self.model_cls(**raw)


class LogicalSwitchPort(LogicalSwitchPortColumns, Model):
    objects: LogicalSwitchPortManager

    def plug(self, port: "LogicalRouterPort") -> None:
        """Attach this switch port to a logical router port.

        The switch port becomes a ``router`` type port whose L2/L3 addresses
        are taken from the peer router port (``addresses = {"router"}``), wired
        through the ``router-port`` option.
        """
        from ovn.models.logical_router_port import LogicalRouterPort

        if not isinstance(port, LogicalRouterPort):
            return

        self.type = "router"
        self.addresses = {"router"}
        options = dict(getattr(self, "options", None) or {})
        options["router-port"] = port.name
        self.options = options
        self.save()
