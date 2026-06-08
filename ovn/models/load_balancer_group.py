from ovn.models._columns import LoadBalancerGroupColumns
from ovn.models.base import Model


class LoadBalancerGroup(LoadBalancerGroupColumns, Model):
    pass
