from ovn.models._columns import LoadBalancerColumns
from ovn.models.base import Model


class LoadBalancer(LoadBalancerColumns, Model):
    pass
