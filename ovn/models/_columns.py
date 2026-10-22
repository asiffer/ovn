import typing


class ACLColumns:
    name: typing.Optional[str]
    """OVSDB type: optional string."""
    priority: int
    """OVSDB type: integer."""
    sample_est: typing.Optional[str]
    """Python representation: optional string."""
    log: bool
    """OVSDB type: boolean."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    sample_new: typing.Optional[str]
    """Python representation: optional string."""
    direction: typing.Literal["from-lport", "to-lport"]
    """OVSDB type: string."""
    meter: typing.Optional[str]
    """OVSDB type: optional string."""
    options: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    label: int
    """OVSDB type: integer."""
    action: typing.Literal[
        "allow", "allow-related", "allow-stateless", "drop", "pass", "reject"
    ]
    """OVSDB type: string."""
    match: str
    """OVSDB type: string."""
    severity: typing.Optional[
        typing.Literal["alert", "debug", "info", "notice", "warning"]
    ]
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
    addresses: typing.Set[str]
    """OVSDB type: set of string."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class BFDColumns:
    logical_port: str
    """OVSDB type: string."""
    status: typing.Optional[typing.Literal["admin_down", "down", "init", "up"]]
    """OVSDB type: optional string."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    options: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    min_tx: typing.Optional[int]
    """OVSDB type: optional integer."""
    dst_ip: str
    """OVSDB type: string."""
    detect_mult: typing.Optional[int]
    """OVSDB type: optional integer."""
    min_rx: typing.Optional[int]
    """OVSDB type: optional integer."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class ChassisTemplateVarColumns:
    chassis: str
    """OVSDB type: string."""
    variables: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    external_ids: typing.Dict[str, str]
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
    other_config: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    status: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    max_backoff: typing.Optional[int]
    """OVSDB type: optional integer."""
    inactivity_probe: typing.Optional[int]
    """OVSDB type: optional integer."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class CoppColumns:
    name: str
    """OVSDB type: string."""
    meters: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class DHCPOptionsColumns:
    cidr: str
    """OVSDB type: string."""
    options: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class DHCPRelayColumns:
    name: str
    """Python representation: string."""
    servers: typing.Optional[str]
    """Python representation: optional string."""
    options: typing.Dict[str, str]
    """Python representation: map of string to string."""
    external_ids: typing.Dict[str, str]
    """Python representation: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class DNSColumns:
    records: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    options: typing.Dict[str, str]
    """Python representation: map of string to string."""
    external_ids: typing.Dict[str, str]
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
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    child_port: typing.Set[str]
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
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    options: typing.Dict[str, str]
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
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class HAChassisGroupColumns:
    name: str
    """OVSDB type: string."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    ha_chassis: typing.Set[str]
    """OVSDB type: set of UUID references to HA_Chassis (strong)."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LoadBalancerColumns:
    health_check: typing.Set[str]
    """OVSDB type: set of UUID references to Load_Balancer_Health_Check (strong)."""
    name: str
    """OVSDB type: string."""
    protocol: typing.Optional[typing.Literal["sctp", "tcp", "udp"]]
    """OVSDB type: optional string."""
    selection_fields: typing.Set[
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
    options: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    ip_port_mappings: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    vips: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LoadBalancerGroupColumns:
    name: str
    """OVSDB type: string."""
    load_balancer: typing.Set[str]
    """OVSDB type: set of UUID references to Load_Balancer (weak)."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LoadBalancerHealthCheckColumns:
    vip: str
    """OVSDB type: string."""
    options: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LogicalRouterColumns:
    name: str
    """OVSDB type: string."""
    policies: typing.Set[str]
    """OVSDB type: set of UUID references to Logical_Router_Policy (strong)."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    options: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    enabled: typing.Optional[bool]
    """OVSDB type: optional boolean."""
    nat: typing.Set[str]
    """OVSDB type: set of UUID references to NAT (strong)."""
    load_balancer: typing.Set[str]
    """OVSDB type: set of UUID references to Load_Balancer (weak)."""
    load_balancer_group: typing.Set[str]
    """OVSDB type: set of UUID references to Load_Balancer_Group (strong)."""
    static_routes: typing.Set[str]
    """OVSDB type: set of UUID references to Logical_Router_Static_Route (strong)."""
    ports: typing.Set[str]
    """OVSDB type: set of UUID references to Logical_Router_Port (strong)."""
    copp: typing.Optional[str]
    """OVSDB type: optional UUID reference to Copp (weak)."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LogicalRouterPolicyColumns:
    priority: int
    """OVSDB type: integer."""
    chain: typing.Optional[str]
    """Python representation: optional string."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    options: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    jump_chain: typing.Optional[str]
    """Python representation: optional string."""
    bfd_sessions: typing.Set[str]
    """Python representation: set of string values."""
    match: str
    """OVSDB type: string."""
    action: typing.Literal["allow", "drop", "jump", "reroute"]
    """OVSDB type: string."""
    nexthop: typing.Optional[str]
    """OVSDB type: optional string."""
    nexthops: typing.Set[str]
    """OVSDB type: set of string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LogicalRouterPortColumns:
    name: str
    """OVSDB type: string."""
    ipv6_prefix: typing.Set[str]
    """OVSDB type: set of string."""
    mac: str
    """OVSDB type: string."""
    gateway_chassis: typing.Set[str]
    """OVSDB type: set of UUID references to Gateway_Chassis (strong)."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    options: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    ha_chassis_group: typing.Optional[str]
    """OVSDB type: optional UUID reference to HA_Chassis_Group (strong)."""
    status: typing.Dict[str, str]
    """Python representation: map of string to string."""
    enabled: typing.Optional[bool]
    """OVSDB type: optional boolean."""
    networks: typing.Set[str]
    """OVSDB type: set of string."""
    peer: typing.Optional[str]
    """OVSDB type: optional string."""
    dhcp_relay: typing.Optional[str]
    """Python representation: optional string."""
    ipv6_ra_configs: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LogicalRouterStaticRouteColumns:
    selection_fields: typing.Set[
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
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    options: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    bfd: typing.Optional[str]
    """OVSDB type: optional UUID reference to BFD (weak)."""
    ip_prefix: str
    """OVSDB type: string."""
    route_table: str
    """OVSDB type: string."""
    nexthop: str
    """OVSDB type: string."""
    output_port: typing.Optional[str]
    """OVSDB type: optional string."""
    policy: typing.Optional[typing.Literal["dst-ip", "src-ip"]]
    """OVSDB type: optional string."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LogicalSwitchColumns:
    name: str
    """OVSDB type: string."""
    qos_rules: typing.Set[str]
    """OVSDB type: set of UUID references to QoS (strong)."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    other_config: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    dns_records: typing.Set[str]
    """OVSDB type: set of UUID references to DNS (weak)."""
    ports: typing.Set[str]
    """OVSDB type: set of UUID references to Logical_Switch_Port (strong)."""
    load_balancer: typing.Set[str]
    """OVSDB type: set of UUID references to Load_Balancer (weak)."""
    load_balancer_group: typing.Set[str]
    """OVSDB type: set of UUID references to Load_Balancer_Group (strong)."""
    forwarding_groups: typing.Set[str]
    """OVSDB type: set of UUID references to Forwarding_Group (strong)."""
    copp: typing.Optional[str]
    """OVSDB type: optional UUID reference to Copp (weak)."""
    acls: typing.Set[str]
    """OVSDB type: set of UUID references to ACL (strong)."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class LogicalSwitchPortColumns:
    name: str
    """OVSDB type: string."""
    ha_chassis_group: typing.Optional[str]
    """OVSDB type: optional UUID reference to HA_Chassis_Group (strong)."""
    options: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    parent_name: typing.Optional[str]
    """OVSDB type: optional string."""
    enabled: typing.Optional[bool]
    """OVSDB type: optional boolean."""
    type: str
    """OVSDB type: string."""
    dhcpv6_options: typing.Optional[str]
    """OVSDB type: optional UUID reference to DHCP_Options (weak)."""
    peer: typing.Optional[str]
    """Python representation: optional string."""
    addresses: typing.Set[str]
    """OVSDB type: set of string."""
    tag: typing.Optional[int]
    """OVSDB type: optional integer."""
    up: typing.Optional[bool]
    """OVSDB type: optional boolean."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    tag_request: typing.Optional[int]
    """OVSDB type: optional integer."""
    port_security: typing.Set[str]
    """OVSDB type: set of string."""
    dhcpv4_options: typing.Optional[str]
    """OVSDB type: optional UUID reference to DHCP_Options (weak)."""
    mirror_rules: typing.Set[str]
    """OVSDB type: set of UUID references to Mirror (weak)."""
    dynamic_addresses: typing.Optional[str]
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
    fair: typing.Optional[bool]
    """OVSDB type: optional boolean."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    bands: typing.Set[str]
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
    external_ids: typing.Dict[str, str]
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
    external_ids: typing.Dict[str, str]
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
    gateway_port: typing.Optional[str]
    """OVSDB type: optional UUID reference to Logical_Router_Port (weak)."""
    priority: int
    """Python representation: integer."""
    external_port_range: str
    """OVSDB type: string."""
    logical_port: typing.Optional[str]
    """OVSDB type: optional string."""
    options: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    exempted_ext_ips: typing.Optional[str]
    """OVSDB type: optional UUID reference to Address_Set (strong)."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    allowed_ext_ips: typing.Optional[str]
    """OVSDB type: optional UUID reference to Address_Set (strong)."""
    type: typing.Literal["dnat", "dnat_and_snat", "snat"]
    """OVSDB type: string."""
    external_ip: str
    """OVSDB type: string."""
    match: str
    """Python representation: string."""
    external_mac: typing.Optional[str]
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
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    options: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    ssl: typing.Optional[str]
    """OVSDB type: optional UUID reference to SSL (strong)."""
    ipsec: bool
    """OVSDB type: boolean."""
    hv_cfg_timestamp: int
    """OVSDB type: integer."""
    connections: typing.Set[str]
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
    ports: typing.Set[str]
    """OVSDB type: set of UUID references to Logical_Switch_Port (weak)."""
    external_ids: typing.Dict[str, str]
    """OVSDB type: map of string to string."""
    acls: typing.Set[str]
    """OVSDB type: set of UUID references to ACL (strong)."""
    _uuid: str
    """OVSDB type: generated, immutable UUID row identifier."""
    _version: str
    """OVSDB type: ephemeral UUID version token, changed on row updates."""


class QoSColumns:
    action: typing.Dict[typing.Literal["dscp", "mark"], int]
    """OVSDB type: map of string to integer."""
    match: str
    """OVSDB type: string."""
    bandwidth: typing.Dict[typing.Literal["burst", "rate"], int]
    """OVSDB type: map of string to integer."""
    priority: int
    """OVSDB type: integer."""
    direction: typing.Literal["from-lport", "to-lport"]
    """OVSDB type: string."""
    external_ids: typing.Dict[str, str]
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
    external_ids: typing.Dict[str, str]
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
    collectors: typing.Set[str]
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
    external_ids: typing.Dict[str, str]
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
    external_ids: typing.Dict[str, str]
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
