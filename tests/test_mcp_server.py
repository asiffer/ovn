from types import SimpleNamespace

import pytest

pytest.importorskip("mcp")

from ovn.mcp_server import (
    _dump_model,
    create_logical_router_port,
    create_logical_switch,
    create_logical_switch_port,
    delete_logical_switch,
    get_logical_switch,
    list_logical_router_ports,
    list_logical_switch_ports,
    list_logical_switches,
)
from ovn.models import (
    LogicalRouter,
    LogicalRouterPort,
    LogicalSwitch,
    LogicalSwitchPort,
)
from ovn.models.base import Model


def fake_model(**attributes):
    return SimpleNamespace(**attributes, fields=list(attributes))


def test_list_logical_switches(monkeypatch):
    switches = [
        fake_model(_uuid="uuid-1", name="switch-1"),
        fake_model(_uuid="uuid-2", name="switch-2"),
    ]
    monkeypatch.setattr(LogicalSwitch.objects, "list", lambda: switches)

    assert list_logical_switches() == [
        {"_uuid": "uuid-1", "name": "switch-1"},
        {"_uuid": "uuid-2", "name": "switch-2"},
    ]


def test_get_logical_switch(monkeypatch):
    switch = fake_model(_uuid="uuid-1", name="switch-1")
    monkeypatch.setattr(
        LogicalSwitch.objects,
        "get_by_name",
        lambda name: switch if name == "switch-1" else None,
    )

    assert get_logical_switch("switch-1") == {
        "_uuid": "uuid-1",
        "name": "switch-1",
    }
    assert get_logical_switch("missing") is None


def test_create_logical_switch(monkeypatch):
    switch = fake_model(_uuid="uuid-1", name="switch-1")
    monkeypatch.setattr(
        LogicalSwitch.objects,
        "create",
        lambda **kwargs: switch if kwargs == {"name": "switch-1"} else None,
    )

    assert create_logical_switch("switch-1") == {
        "_uuid": "uuid-1",
        "name": "switch-1",
    }


def test_delete_logical_switch(monkeypatch):
    switch = SimpleNamespace(_uuid="uuid-1", name="switch-1", delete=lambda: None)
    monkeypatch.setattr(
        LogicalSwitch.objects,
        "get",
        lambda uuid: switch if uuid == "uuid-1" else None,
    )

    assert delete_logical_switch("uuid-1") is True
    assert delete_logical_switch("missing") is False


def test_dump_model_converts_sets_to_json_lists(monkeypatch):
    monkeypatch.setattr(
        Model, "fields", property(lambda self: ["_uuid", "name", "ports"])
    )
    model = LogicalSwitch.__new__(LogicalSwitch)
    model._uuid = "uuid-1"
    model.ports = {"port-1", "port-2"}
    model.name = "switch-1"

    assert _dump_model(model) == {
        "_uuid": "uuid-1",
        "name": "switch-1",
        "ports": ["port-1", "port-2"],
    }


def test_list_logical_switch_ports(monkeypatch):
    switch = SimpleNamespace(ports={"port-1"})
    ports = [
        fake_model(_uuid="port-1", name="attached"),
        fake_model(_uuid="port-2", name="other"),
    ]
    monkeypatch.setattr(LogicalSwitch.objects, "get", lambda uuid: switch)
    monkeypatch.setattr(LogicalSwitchPort.objects, "list", lambda: ports)

    assert list_logical_switch_ports("switch-1") == [
        {"_uuid": "port-1", "name": "attached"}
    ]


def test_create_logical_switch_port(monkeypatch):
    switch = SimpleNamespace(
        create_port=lambda **kwargs: SimpleNamespace(
            _uuid="port-1",
            name=kwargs["name"],
            addresses=kwargs["addresses"],
            fields=["_uuid", "name", "addresses"],
        )
    )
    monkeypatch.setattr(LogicalSwitch.objects, "get", lambda uuid: switch)

    assert create_logical_switch_port(
        "switch-1", "workload", ["00:11:22:33:44:55 10.0.0.2"]
    ) == {
        "_uuid": "port-1",
        "name": "workload",
        "addresses": ["00:11:22:33:44:55 10.0.0.2"],
    }


def test_list_logical_router_ports(monkeypatch):
    router = SimpleNamespace(ports={"port-1"})
    ports = [fake_model(_uuid="port-1", name="router-port")]
    monkeypatch.setattr(LogicalRouter.objects, "get", lambda uuid: router)
    monkeypatch.setattr(LogicalRouterPort.objects, "list", lambda: ports)

    assert list_logical_router_ports("router-1") == [
        {"_uuid": "port-1", "name": "router-port"}
    ]


def test_create_logical_router_port(monkeypatch):
    router = SimpleNamespace(
        create_port=lambda **kwargs: fake_model(_uuid="port-1", **kwargs)
    )
    monkeypatch.setattr(LogicalRouter.objects, "get", lambda uuid: router)

    assert create_logical_router_port(
        "router-1", "router-port", "00:11:22:33:44:55", ["10.0.0.1/24"]
    ) == {
        "_uuid": "port-1",
        "name": "router-port",
        "mac": "00:11:22:33:44:55",
        "networks": ["10.0.0.1/24"],
    }
