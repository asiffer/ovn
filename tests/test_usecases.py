from typing import cast

import pytest

import ovn.usecases as usecases
from ovn.models import DHCPOptions, LogicalRouter, LogicalSwitch, PortGroup


class FakeRow:
    next_uuid = 0
    _uuid: str
    name: str
    acls: set[str]

    def __init__(self, **attributes):
        self.__dict__.update(attributes)

    def save(self):
        if not hasattr(self, "_uuid"):
            type(self).next_uuid += 1
            self._uuid = f"uuid-{type(self).next_uuid}"


class FakePort(FakeRow):
    type: str
    addresses: set[str]
    options: dict[str, str]
    networks: set[str]
    port_security: set[str]
    dhcpv4_options: str

    def plug(self, router_port):
        self.type = "router"
        self.addresses = {"router"}
        self.options = {"router-port": router_port.name}
        self.save()


class FakeSwitch(FakeRow):
    other_config: dict[str, str]
    load_balancer: set[str]

    def create_port(self, **attributes):
        port = FakePort(**attributes)
        port.save()
        return port


class FakeRouter(FakeRow):
    nat: set[str]

    def create_port(self, **attributes):
        port = FakePort(**attributes)
        port.save()
        return port


@pytest.fixture
def fake_models(monkeypatch):
    for name, model in {
        "ACL": FakeRow,
        "DHCPOptions": FakeRow,
        "LoadBalancer": FakeRow,
        "LogicalRouter": FakeRouter,
        "LogicalSwitch": FakeSwitch,
        "NAT": FakeRow,
        "PortGroup": FakeRow,
    }.items():
        monkeypatch.setattr(usecases, name, model)


def test_create_network_segment_with_dhcp(fake_models):
    router = FakeRouter(name="router")
    router.save()

    segment = usecases.create_network_segment(
        name="app",
        subnet="10.0.1.0/24",
        gateway="10.0.1.1",
        router=cast(LogicalRouter, router),
        router_port_mac="00:11:22:33:44:55",
        dhcp_options={"server_id": "10.0.1.1"},
    )

    assert segment.switch.other_config == {"subnet": "10.0.1.0/24"}
    assert segment.router_port.networks == {"10.0.1.1/24"}
    assert segment.switch_router_port.options == {
        "router-port": "app-router",
    }
    assert segment.dhcp_options is not None
    assert segment.dhcp_options.cidr == "10.0.1.0/24"


def test_create_network_segment_rejects_gateway_outside_subnet(fake_models):
    with pytest.raises(ValueError, match="inside subnet"):
        usecases.create_network_segment(
            name="app",
            subnet="10.0.1.0/24",
            gateway="10.0.2.1",
            router=cast(LogicalRouter, FakeRouter(name="router")),
            router_port_mac="00:11:22:33:44:55",
        )


def test_attach_workload_supports_static_and_dhcp(fake_models):
    switch = FakeSwitch(name="app")
    dhcp = FakeRow()
    dhcp.save()

    static_port = usecases.attach_workload(
        cast(LogicalSwitch, switch),
        name="static-vm",
        mac="00:11:22:33:44:66",
        ip_address="10.0.1.10",
    )
    dynamic_port = usecases.attach_workload(
        cast(LogicalSwitch, switch),
        name="dhcp-vm",
        mac="00:11:22:33:44:77",
        dhcp_options=cast(DHCPOptions, dhcp),
    )

    assert static_port.addresses == {"00:11:22:33:44:66 10.0.1.10"}
    assert static_port.port_security == static_port.addresses
    assert dynamic_port.addresses == {"dynamic"}
    assert dynamic_port.dhcpv4_options == dhcp._uuid


def test_attach_workload_requires_exactly_one_address_mode(fake_models):
    switch = FakeSwitch(name="app")
    with pytest.raises(ValueError, match="exactly one"):
        usecases.attach_workload(
            cast(LogicalSwitch, switch), name="vm", mac="00:11:22:33:44:66"
        )


def test_create_tenant_network(fake_models):
    tenant = usecases.create_tenant_network(
        name="tenant",
        subnet="192.0.2.0/24",
        gateway="192.0.2.1",
        router_port_mac="00:11:22:33:44:55",
    )

    assert tenant.router.name == "tenant-router"
    assert tenant.segment.switch.name == "tenant"


def test_configure_outbound_nat_attaches_rule_to_router(fake_models):
    router = FakeRouter(name="tenant-router", nat=set())
    router.save()

    nat = usecases.configure_outbound_nat(
        cast(LogicalRouter, router),
        logical_ip="10.0.1.0/24",
        external_ip="192.0.2.10",
    )

    assert nat.type == "snat"
    assert nat.logical_ip == "10.0.1.0/24"
    assert router.nat == {nat._uuid}


def test_apply_security_policy_attaches_acl_rows(fake_models):
    port_group = FakeRow(name="web")
    port_group.save()

    acls = usecases.allow_web_traffic(cast(PortGroup, port_group))

    assert len(acls) == 2
    assert port_group.acls == {acl._uuid for acl in acls}
    assert {acl.match for acl in acls} == {
        "ip && tcp && tcp.dst == 80",
        "ip && tcp && tcp.dst == 443",
    }


def test_create_service_endpoint_attaches_load_balancer(fake_models):
    switch = FakeSwitch(name="app", load_balancer=set())

    lb = usecases.create_service_endpoint(
        name="web",
        vip="192.0.2.20:80",
        backends=["10.0.1.10:80", "10.0.1.11:80"],
        switches=[cast(LogicalSwitch, switch)],
    )

    assert lb.vips == {
        "192.0.2.20:80": "10.0.1.10:80,10.0.1.11:80",
    }
    assert switch.load_balancer == {lb._uuid}
