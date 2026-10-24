# OVN

Script [Open Virtual Network](https://github.com/ovn-org/ovn) with Python.

Most tools for deploying infrastructure (the whole Infrastructure-as-Code
ecosystem) take a *declarative* approach: you hand them a configuration file and
they reconcile the world to match it. `ovn` (a.k.a. **ovn**) takes the other
road — it lets you **script** an OVN network from Python, with a Django-like ORM
over the OVN **Northbound** database.

It is a pure [OVSDB](https://datatracker.ietf.org/doc/html/rfc7047) client
(JSON-RPC over a socket): it talks directly to the Northbound DB and lets OVN do
the rest. There is **no dependency on the `ovn`/`ovs` C tooling** at runtime.

## Install

```shell
pip install ovn
```

## Quick example

```python
from ovn.models import LogicalRouter, LogicalSwitch

# create a network object
switch = LogicalSwitch(name="sw0")
# save it to the OVN database (yes, OVN works like that)
switch.save()

# another object
router = LogicalRouter(name="ro0")
router.save()

# connect them!
switch.plug(router,
            mac="00:11:22:33:44:55",
            networks="192.168.100.1/24")
```

Each OVN Northbound table maps to a model class, and every class exposes a
Django-style `.objects` manager:

```python
from ovn.models import LogicalSwitch

LogicalSwitch.objects.create(name="sw1")     # insert
LogicalSwitch.objects.list()                 # SELECT *
sw = LogicalSwitch.objects.get_by_name("sw1")
sw.delete()
```

An instance is just a row. Set attributes and call `save()` to sync; call
`fetch()` (or `refresh_from_db()`) to reload from the database.

## High-level network shortcuts

The `ovn.shortcuts` module composes models for common workflows while leaving
the regular model API available. For example, create a tenant router and routed
segment, then attach a DHCP-addressed workload:

```python
from ovn.shortcuts import attach_workload, create_tenant_network

tenant = create_tenant_network(
    name="app",
    subnet="10.0.1.0/24",
    gateway="10.0.1.1",
    router_port_mac="00:11:22:33:44:55",
    dhcp_options={
        "server_id": "10.0.1.1",
        "server_mac": "00:11:22:33:44:55",
        "lease_time": "3600",
    },
)
assert tenant.segment.dhcp_options is not None
workload_port = attach_workload(
    tenant.segment.switch,
    name="app-vm1",
    mac="00:11:22:33:44:66",
    dhcp_options=tenant.segment.dhcp_options,
)
```

| Helper                         | Description                                                                                                                  |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `create_network_segment(...)`  | Creates a logical switch and connects it to an existing router. Can also create DHCP options for the subnet.                 |
| `create_tenant_network(...)`   | Creates a router and one routed segment.                                                                                     |
| `attach_workload(...)`         | Attaches a switch port with either a static `ip_address` or `dhcp_options`; provide exactly one.                             |
| `configure_outbound_nat(...)`  | Creates and attaches a source-NAT rule to a router. Does not create an external network, router interface, or default route. |
| `configure_static_route(...)`  | Adds a static route to a router after validating destination and next-hop IP versions.                                       |
| `apply_security_policy(...)`   | Attaches caller-defined `ACLRule` rules to a port group.                                                                     |
| `allow_web_traffic(...)`       | A preset security policy for TCP ports 80 and 443.                                                                           |
| `create_service_endpoint(...)` | Creates a load balancer and attaches it to selected switches and/or routers. VIP and backends use OVN's `IP:port` format.    |

Helpers return the created model instances (or workflow dataclasses) for
further customization. Multi-step workflows perform several database
operations and are not atomic; a failure can leave earlier rows in place.

## Configuration

The server address is read from the `OVN_NB_DB` environment variable (default
`unix:/run/ovn/ovnnb_db.sock`). Two formats are accepted:

```shell
export OVN_NB_DB=unix:/run/ovn/ovnnb_db.sock   # local socket
export OVN_NB_DB=tcp:127.0.0.1:6641            # remote / TCP
```

> Importing `ovn.models` never touches the database. The schema is fetched (and
> cached) lazily on first real use, so imports, `--help`, and test collection
> all work without a reachable DB.

## CLI

The package installs an `ovn` console script:

```shell
ovn shell     # IPython shell with every model preloaded
ovn schema    # dump the live Northbound schema as JSON
```

## Docker network driver (optional)

With the `docker` extra installed (`pip install "ovn[docker]"`), `ovn` can act
as a [libnetwork remote driver](https://github.com/moby/moby/blob/master/libnetwork/docs/remote.md),
backing Docker networks with OVN logical switches on a single host:

```shell
ovn-docker-driver
# then, on the same host:
docker network create -d ovn mynet
```

The `CreateNetwork` API methods translates into a `Logical_Switch`, each container gets a
`Logical_Switch_Port` bound to the local integration bridge (`br-int`). See
[`ovn/docker.py`](ovn/docker.py) for the full mapping.

## Architecture

It helps to understand the overall architecture of OVN first — see the
[official documentation](https://www.ovn.org/support/dist-docs/ovn-architecture.7.html),
summed up below.

![](assets/architecture/overall.png)

`ovn` is a thin OVN Northbound client. It manages the database; OVN does the
rest.


Internally it is layered low → high:

| Layer         | Module           | Role                                                    |
| ------------- | ---------------- | ------------------------------------------------------- |
| Wire protocol | `ovn/ovsdb/`     | raw OVSDB JSON-RPC (`transport`, `ovsdb_client`)        |
| Schema        | `ovn/schema.py`  | pydantic models of the OVSDB schema + (de)serialization |
| Client        | `ovn/client.py`  | `OVNClient` + transaction composer for `OVN_Northbound` |
| Manager       | `ovn/manager.py` | `Manager[T]`: the `.objects` query/CRUD interface       |
| Models        | `ovn/models/`    | one thin class per Northbound table                     |

## Development

The project uses [uv](https://docs.astral.sh/uv/) and targets Python ≥ 3.12.

```shell
uv sync
uv run pytest        # transport tests need no DB; model/client tests need one
```

A local OVN Northbound DB is needed for anything touching models or the client.
Spin one up with the bundled compose file:

```shell
cd docker && docker compose up --build   # NB DB on 127.0.0.1:6641
export OVN_NB_DB=tcp:127.0.0.1:6641
```

## License

MIT
