from ovn.models._columns import LoadBalancerHealthCheckColumns
from ovn.models.base import Model


class LoadBalancerHealthCheck(LoadBalancerHealthCheckColumns, Model):
    pass
