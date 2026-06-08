from ovn.models._columns import QoSColumns
from ovn.models.base import Model


class QoS(QoSColumns, Model):
    __table__ = "QoS"
