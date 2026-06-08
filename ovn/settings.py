from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    ovn_northbound: str = Field(
        "unix:/run/ovn/ovnnb_db.sock",
        alias="OVN_NB_DB",
        examples=["unix:/run/ovn/ovnnb_db.sock", "tcp:127.0.0.1:6641"],
    )


class DriverSettings(BaseSettings):
    """Configuration for the Docker network plugin (``ovn.docker``).

    Each field is read from its environment variable (the ``alias``) and may be
    overridden by the matching CLI flag of ``python -m ovn.docker``.
    """

    model_config = SettingsConfigDict()

    socket: str = Field(
        "/run/docker/plugins/ovn.sock",
        alias="OVN_PLUGIN_SOCKET",
        examples=["unix:/run/docker/plugins/ovn.sock", "tcp:127.0.0.1:9000"],
    )
    bridge: str = Field(
        "br-int",
        alias="OVN_BRIDGE",
        description="Local OVN integration bridge to plug container veths into.",
    )
    ovs_db: str = Field(
        "unix:/var/run/openvswitch/db.sock",
        alias="OVS_DB",
        examples=["unix:/var/run/openvswitch/db.sock", "tcp:127.0.0.1:6640"],
        description="Local Open vSwitch OVSDB socket (where the br-int port lives).",
    )
