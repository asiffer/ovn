import typing


class ACLColumns:
    name: str | None
    """OVSDB type: optional string."""
    priority: int
    """OVSDB type: integer."""
    sample_est: str | None
    """Python representation: optional string."""
    log: bool
    """OVSDB type: boolean."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    sample_new: str | None
    """Python representation: optional string."""
    direction: typing.Literal["from-lport", "to-lport"]
    """OVSDB type: string."""
    meter: str | None
    """OVSDB type: optional string."""
    options: dict[str, str]
    """OVSDB type: map of string to string."""
    label: int
    """OVSDB type: integer."""
    action: typing.Literal[
        "allow", "allow-related", "allow-stateless", "drop", "pass", "reject"
    ]
    """OVSDB type: string."""
    match: str
    """OVSDB type: string."""
    severity: typing.Literal["alert", "debug", "info", "notice", "warning"] | None
    """OVSDB type: optional string."""
    tier: int
    """Python representation: integer."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class AddressSetColumns:
    name: str
    """OVSDB type: string."""
    addresses: set[str]
    """OVSDB type: set of string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class BFDColumns:
    logical_port: str
    """OVSDB type: string."""
    status: typing.Literal["admin_down", "down", "init", "up"] | None
    """OVSDB type: optional string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    options: dict[str, str]
    """OVSDB type: map of string to string."""
    min_tx: int | None
    """OVSDB type: optional integer."""
    dst_ip: str
    """OVSDB type: string."""
    detect_mult: int | None
    """OVSDB type: optional integer."""
    min_rx: int | None
    """OVSDB type: optional integer."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class ChassisTemplateVarColumns:
    chassis: str
    """OVSDB type: string."""
    variables: dict[str, str]
    """OVSDB type: map of string to string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class ConnectionColumns:
    is_connected: bool
    """OVSDB type: boolean."""
    target: str
    """OVSDB type: string."""
    other_config: dict[str, str]
    """OVSDB type: map of string to string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    status: dict[str, str]
    """OVSDB type: map of string to string."""
    max_backoff: int | None
    """OVSDB type: optional integer."""
    inactivity_probe: int | None
    """OVSDB type: optional integer."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class CoppColumns:
    name: str
    """OVSDB type: string."""
    meters: dict[str, str]
    """OVSDB type: map of string to string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class DHCPOptionsColumns:
    cidr: str
    """OVSDB type: string."""
    options: dict[str, str]
    """OVSDB type: map of string to string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class DHCPRelayColumns:
    name: str
    """Python representation: string."""
    servers: str | None
    """Python representation: optional string."""
    options: dict[str, str]
    """Python representation: map of string to string."""
    external_ids: dict[str, str]
    """Python representation: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class DNSColumns:
    records: dict[str, str]
    """OVSDB type: map of string to string."""
    options: dict[str, str]
    """Python representation: map of string to string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class ForwardingGroupColumns:
    liveness: bool
    """OVSDB type: boolean."""
    name: str
    """OVSDB type: string."""
    vip: str
    """OVSDB type: string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    child_port: set[str]
    """OVSDB type: set of string."""
    vmac: str
    """OVSDB type: string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class GatewayChassisColumns:
    name: str
    """OVSDB type: string."""
    priority: int
    """OVSDB type: integer."""
    chassis_name: str
    """OVSDB type: string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    options: dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class HAChassisColumns:
    priority: int
    """OVSDB type: integer."""
    chassis_name: str
    """OVSDB type: string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class HAChassisGroupColumns:
    name: str
    """OVSDB type: string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    ha_chassis: set[str]
    """OVSDB type: set of UUID references to HA_Chassis (strong)."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LoadBalancerColumns:
    health_check: set[str]
    """OVSDB type: set of UUID references to Load_Balancer_Health_Check (strong)."""
    name: str
    """OVSDB type: string."""
    protocol: typing.Literal["sctp", "tcp", "udp"] | None
    """OVSDB type: optional string."""
    selection_fields: set[
        typing.Literal[
            "eth_dst",
            "eth_src",
            "ip_dst",
            "ip_src",
            "ipv6_dst",
            "ipv6_src",
            "tp_dst",
            "tp_src",
        ]
    ]
    """OVSDB type: set of string."""
    options: dict[str, str]
    """OVSDB type: map of string to string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    ip_port_mappings: dict[str, str]
    """OVSDB type: map of string to string."""
    vips: dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LoadBalancerGroupColumns:
    name: str
    """OVSDB type: string."""
    load_balancer: set[str]
    """OVSDB type: set of UUID references to Load_Balancer (weak)."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LoadBalancerHealthCheckColumns:
    vip: str
    """OVSDB type: string."""
    options: dict[str, str]
    """OVSDB type: map of string to string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LogicalRouterColumns:
    name: str
    """OVSDB type: string."""
    policies: set[str]
    """OVSDB type: set of UUID references to Logical_Router_Policy (strong)."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    options: dict[str, str]
    """OVSDB type: map of string to string."""
    enabled: bool | None
    """OVSDB type: optional boolean."""
    nat: set[str]
    """OVSDB type: set of UUID references to NAT (strong)."""
    load_balancer: set[str]
    """OVSDB type: set of UUID references to Load_Balancer (weak)."""
    load_balancer_group: set[str]
    """OVSDB type: set of UUID references to Load_Balancer_Group (strong)."""
    static_routes: set[str]
    """OVSDB type: set of UUID references to Logical_Router_Static_Route (strong)."""
    ports: set[str]
    """OVSDB type: set of UUID references to Logical_Router_Port (strong)."""
    copp: str | None
    """OVSDB type: optional UUID reference to Copp (weak)."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LogicalRouterPolicyColumns:
    priority: int
    """OVSDB type: integer."""
    chain: str | None
    """Python representation: optional string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    options: dict[str, str]
    """OVSDB type: map of string to string."""
    jump_chain: str | None
    """Python representation: optional string."""
    bfd_sessions: set[str]
    """Python representation: set of string values."""
    match: str
    """OVSDB type: string."""
    action: typing.Literal["allow", "drop", "jump", "reroute"]
    """OVSDB type: string."""
    nexthop: str | None
    """OVSDB type: optional string."""
    nexthops: set[str]
    """OVSDB type: set of string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LogicalRouterPortColumns:
    name: str
    """OVSDB type: string."""
    ipv6_prefix: set[str]
    """OVSDB type: set of string."""
    mac: str
    """OVSDB type: string."""
    gateway_chassis: set[str]
    """OVSDB type: set of UUID references to Gateway_Chassis (strong)."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    options: dict[str, str]
    """OVSDB type: map of string to string."""
    ha_chassis_group: str | None
    """OVSDB type: optional UUID reference to HA_Chassis_Group (strong)."""
    status: dict[str, str]
    """Python representation: map of string to string."""
    enabled: bool | None
    """OVSDB type: optional boolean."""
    networks: set[str]
    """OVSDB type: set of string."""
    peer: str | None
    """OVSDB type: optional string."""
    dhcp_relay: str | None
    """Python representation: optional string."""
    ipv6_ra_configs: dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LogicalRouterStaticRouteColumns:
    selection_fields: set[
        typing.Literal[
            "eth_dst",
            "eth_src",
            "ip_dst",
            "ip_proto",
            "ip_src",
            "ipv6_dst",
            "ipv6_src",
            "tp_dst",
            "tp_src",
        ]
    ]
    """Python representation: set of string enum ('eth_dst', 'eth_src', 'ip_dst', 'ip_proto', 'ip_src', 'ipv6_dst', 'ipv6_src', 'tp_dst', 'tp_src') values."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    options: dict[str, str]
    """OVSDB type: map of string to string."""
    bfd: str | None
    """OVSDB type: optional UUID reference to BFD (weak)."""
    ip_prefix: str
    """OVSDB type: string."""
    route_table: str
    """OVSDB type: string."""
    nexthop: str
    """OVSDB type: string."""
    output_port: str | None
    """OVSDB type: optional string."""
    policy: typing.Literal["dst-ip", "src-ip"] | None
    """OVSDB type: optional string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LogicalSwitchColumns:
    name: str
    """OVSDB type: string."""
    qos_rules: set[str]
    """OVSDB type: set of UUID references to QoS (strong)."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    other_config: dict[str, str]
    """OVSDB type: map of string to string."""
    dns_records: set[str]
    """OVSDB type: set of UUID references to DNS (weak)."""
    ports: set[str]
    """OVSDB type: set of UUID references to Logical_Switch_Port (strong)."""
    load_balancer: set[str]
    """OVSDB type: set of UUID references to Load_Balancer (weak)."""
    load_balancer_group: set[str]
    """OVSDB type: set of UUID references to Load_Balancer_Group (strong)."""
    forwarding_groups: set[str]
    """OVSDB type: set of UUID references to Forwarding_Group (strong)."""
    copp: str | None
    """OVSDB type: optional UUID reference to Copp (weak)."""
    acls: set[str]
    """OVSDB type: set of UUID references to ACL (strong)."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LogicalSwitchPortColumns:
    name: str
    """OVSDB type: string."""
    ha_chassis_group: str | None
    """OVSDB type: optional UUID reference to HA_Chassis_Group (strong)."""
    options: dict[str, str]
    """OVSDB type: map of string to string."""
    parent_name: str | None
    """OVSDB type: optional string."""
    enabled: bool | None
    """OVSDB type: optional boolean."""
    type: str
    """OVSDB type: string."""
    dhcpv6_options: str | None
    """OVSDB type: optional UUID reference to DHCP_Options (weak)."""
    peer: str | None
    """Python representation: optional string."""
    addresses: set[str]
    """OVSDB type: set of string."""
    tag: int | None
    """OVSDB type: optional integer."""
    up: bool | None
    """OVSDB type: optional boolean."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    tag_request: int | None
    """OVSDB type: optional integer."""
    port_security: set[str]
    """OVSDB type: set of string."""
    dhcpv4_options: str | None
    """OVSDB type: optional UUID reference to DHCP_Options (weak)."""
    mirror_rules: set[str]
    """OVSDB type: set of UUID references to Mirror (weak)."""
    dynamic_addresses: str | None
    """OVSDB type: optional string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class MeterColumns:
    name: str
    """OVSDB type: string."""
    unit: typing.Literal["kbps", "pktps"]
    """OVSDB type: string."""
    fair: bool | None
    """OVSDB type: optional boolean."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    bands: set[str]
    """OVSDB type: set of UUID references to Meter_Band (strong)."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class MeterBandColumns:
    action: typing.Literal["drop"]
    """OVSDB type: string."""
    rate: int
    """OVSDB type: integer."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    burst_size: int
    """OVSDB type: integer."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class MirrorColumns:
    filter: typing.Literal["both", "from-lport", "to-lport"]
    """OVSDB type: string."""
    name: str
    """OVSDB type: string."""
    sink: str
    """OVSDB type: string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    index: int
    """OVSDB type: integer."""
    type: typing.Literal["erspan", "gre", "local"]
    """OVSDB type: string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class NATColumns:
    gateway_port: str | None
    """OVSDB type: optional UUID reference to Logical_Router_Port (weak)."""
    priority: int
    """Python representation: integer."""
    external_port_range: str
    """OVSDB type: string."""
    logical_port: str | None
    """OVSDB type: optional string."""
    options: dict[str, str]
    """OVSDB type: map of string to string."""
    exempted_ext_ips: str | None
    """OVSDB type: optional UUID reference to Address_Set (strong)."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    allowed_ext_ips: str | None
    """OVSDB type: optional UUID reference to Address_Set (strong)."""
    type: typing.Literal["dnat", "dnat_and_snat", "snat"]
    """OVSDB type: string."""
    external_ip: str
    """OVSDB type: string."""
    match: str
    """Python representation: string."""
    external_mac: str | None
    """OVSDB type: optional string."""
    logical_ip: str
    """OVSDB type: string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class NBGlobalColumns:
    sb_cfg_timestamp: int
    """OVSDB type: integer."""
    name: str
    """OVSDB type: string."""
    hv_cfg: int
    """OVSDB type: integer."""
    nb_cfg: int
    """OVSDB type: integer."""
    sb_cfg: int
    """OVSDB type: integer."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    options: dict[str, str]
    """OVSDB type: map of string to string."""
    ssl: str | None
    """OVSDB type: optional UUID reference to SSL (strong)."""
    ipsec: bool
    """OVSDB type: boolean."""
    hv_cfg_timestamp: int
    """OVSDB type: integer."""
    connections: set[str]
    """OVSDB type: set of UUID references to Connection (strong)."""
    nb_cfg_timestamp: int
    """OVSDB type: integer."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class PortGroupColumns:
    name: str
    """OVSDB type: string."""
    ports: set[str]
    """OVSDB type: set of UUID references to Logical_Switch_Port (weak)."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    acls: set[str]
    """OVSDB type: set of UUID references to ACL (strong)."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class QoSColumns:
    action: dict[typing.Literal["dscp", "mark"], int]
    """OVSDB type: map of string to integer."""
    match: str
    """OVSDB type: string."""
    bandwidth: dict[typing.Literal["burst", "rate"], int]
    """OVSDB type: map of string to integer."""
    priority: int
    """OVSDB type: integer."""
    direction: typing.Literal["from-lport", "to-lport"]
    """OVSDB type: string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class SSLColumns:
    certificate: str
    """OVSDB type: string."""
    ssl_ciphers: str
    """OVSDB type: string."""
    external_ids: dict[str, str]
    """OVSDB type: map of string to string."""
    ssl_ciphersuites: str
    """Python representation: string."""
    bootstrap_ca_cert: bool
    """OVSDB type: boolean."""
    private_key: str
    """OVSDB type: string."""
    ssl_protocols: str
    """OVSDB type: string."""
    ca_cert: str
    """OVSDB type: string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class SampleColumns:
    collectors: set[str]
    """Python representation: set of string values."""
    metadata: int
    """Python representation: integer."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class SampleCollectorColumns:
    name: str
    """Python representation: string."""
    id: int
    """Python representation: integer."""
    set_id: int
    """Python representation: integer."""
    external_ids: dict[str, str]
    """Python representation: map of string to string."""
    probability: int
    """Python representation: integer."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class SamplingAppColumns:
    id: int
    """Python representation: integer."""
    external_ids: dict[str, str]
    """Python representation: map of string to string."""
    type: typing.Literal["acl-est", "acl-new", "drop"]
    """Python representation: string enum ('acl-est', 'acl-new', 'drop')."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class StaticMACBindingColumns:
    ip: str
    """OVSDB type: string."""
    logical_port: str
    """OVSDB type: string."""
    mac: str
    """OVSDB type: string."""
    override_dynamic_mac: bool
    """OVSDB type: boolean."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""
