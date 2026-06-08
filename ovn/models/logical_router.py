from ovn.models._columns import LogicalRouterColumns
from ovn.models.base import Model
from ovn.models.logical_router_port import LogicalRouterPort


class LogicalRouter(LogicalRouterColumns, Model):
    def create_port(self, **kwargs) -> LogicalRouterPort:
        """Create a logical router port attached to this router"""
        return LogicalRouterPort.objects.add_to_logical_router(self, **kwargs)
