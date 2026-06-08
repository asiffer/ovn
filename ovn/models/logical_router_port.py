from typing import TYPE_CHECKING

from ovn.manager import Manager
from ovn.models._columns import LogicalRouterPortColumns
from ovn.models.base import Model

if TYPE_CHECKING:
    from ovn.models.logical_router import LogicalRouter


class LogicalRouterPortManager(Manager):
    def add_to_logical_router(
        self, router: "LogicalRouter", **kwargs
    ) -> "LogicalRouterPort":
        """Create the port and bind it to a logical router"""
        raw, _ = self.client.create_and_bind(
            table_create=self._table,
            row_create=kwargs,
            table_bind=router._table(),
            attr_bind="ports",
            where_bind=[("_uuid", "==", ("uuid", router._uuid))],
        )
        return self.model_cls(**raw)


class LogicalRouterPort(LogicalRouterPortColumns, Model):
    objects: LogicalRouterPortManager
