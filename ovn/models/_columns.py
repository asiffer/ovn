import typing


class ACLColumns:
    name: typing.Optional[str]
    priority: int
    sample_est: typing.Optional[str]
    log: bool
    external_ids: typing.Dict[str, str]
    sample_new: typing.Optional[str]
    direction: typing.Literal["from-lport", "to-lport"]
    meter: typing.Optional[str]
    options: typing.Dict[str, str]
    label: int
    action: typing.Literal[
        "allow", "allow-related", "allow-stateless", "drop", "pass", "reject"
    ]
    match: str
    severity: typing.Optional[
        typing.Literal["alert", "debug", "info", "notice", "warning"]
    ]
    tier: int
    _uuid: str
    _version: str


class AddressSetColumns:
    name: str
    addresses: typing.Set[str]
    external_ids: typing.Dict[str, str]
    _uuid: str
    _version: str


class BFDColumns:
    logical_port: str
    status: typing.Optional[typing.Literal["admin_down", "down", "init", "up"]]
    external_ids: typing.Dict[str, str]
    options: typing.Dict[str, str]
    min_tx: typing.Optional[int]
    dst_ip: str
    detect_mult: typing.Optional[int]
    min_rx: typing.Optional[int]
    _uuid: str
    _version: str


class ChassisTemplateVarColumns:
    chassis: str
    variables: typing.Dict[str, str]
    external_ids: typing.Dict[str, str]
    _uuid: str
    _version: str


class ConnectionColumns:
    is_connected: bool
    target: str
    other_config: typing.Dict[str, str]
    external_ids: typing.Dict[str, str]
    status: typing.Dict[str, str]
    max_backoff: typing.Optional[int]
    inactivity_probe: typing.Optional[int]
    _uuid: str
    _version: str


class CoppColumns:
    name: str
    meters: typing.Dict[str, str]
    external_ids: typing.Dict[str, str]
    _uuid: str
    _version: str


class DHCPOptionsColumns:
    cidr: str
    options: typing.Dict[str, str]
    external_ids: typing.Dict[str, str]
    _uuid: str
    _version: str


class DHCPRelayColumns:
    name: str
    servers: typing.Optional[str]
    options: typing.Dict[str, str]
    external_ids: typing.Dict[str, str]
    _uuid: str
    _version: str


class DNSColumns:
    records: typing.Dict[str, str]
    options: typing.Dict[str, str]
    external_ids: typing.Dict[str, str]
    _uuid: str
    _version: str


class ForwardingGroupColumns:
    liveness: bool
    name: str
    vip: str
    external_ids: typing.Dict[str, str]
    child_port: typing.Set[str]
    vmac: str
    _uuid: str
    _version: str


class GatewayChassisColumns:
    name: str
    priority: int
    chassis_name: str
    external_ids: typing.Dict[str, str]
    options: typing.Dict[str, str]
    _uuid: str
    _version: str


class HAChassisColumns:
    priority: int
    chassis_name: str
    external_ids: typing.Dict[str, str]
    _uuid: str
    _version: str


class HAChassisGroupColumns:
    name: str
    external_ids: typing.Dict[str, str]
    ha_chassis: typing.Set[str]
    _uuid: str
    _version: str


class LoadBalancerColumns:
    health_check: typing.Set[str]
    name: str
    protocol: typing.Optional[typing.Literal["sctp", "tcp", "udp"]]
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
    options: typing.Dict[str, str]
    external_ids: typing.Dict[str, str]
    ip_port_mappings: typing.Dict[str, str]
    vips: typing.Dict[str, str]
    _uuid: str
    _version: str


class LoadBalancerGroupColumns:
    name: str
    load_balancer: typing.Set[str]
    _uuid: str
    _version: str


class LoadBalancerHealthCheckColumns:
    vip: str
    options: typing.Dict[str, str]
    external_ids: typing.Dict[str, str]
    _uuid: str
    _version: str


class LogicalRouterColumns:
    name: str
    policies: typing.Set[str]
    external_ids: typing.Dict[str, str]
    options: typing.Dict[str, str]
    enabled: typing.Optional[bool]
    nat: typing.Set[str]
    load_balancer: typing.Set[str]
    load_balancer_group: typing.Set[str]
    static_routes: typing.Set[str]
    ports: typing.Set[str]
    copp: typing.Optional[str]
    _uuid: str
    _version: str


class LogicalRouterPolicyColumns:
    priority: int
    chain: typing.Optional[str]
    external_ids: typing.Dict[str, str]
    options: typing.Dict[str, str]
    jump_chain: typing.Optional[str]
    bfd_sessions: typing.Set[str]
    match: str
    action: typing.Literal["allow", "drop", "jump", "reroute"]
    nexthop: typing.Optional[str]
    nexthops: typing.Set[str]
    _uuid: str
    _version: str


class LogicalRouterPortColumns:
    name: str
    ipv6_prefix: typing.Set[str]
    mac: str
    gateway_chassis: typing.Set[str]
    external_ids: typing.Dict[str, str]
    options: typing.Dict[str, str]
    ha_chassis_group: typing.Optional[str]
    status: typing.Dict[str, str]
    enabled: typing.Optional[bool]
    networks: typing.Set[str]
    peer: typing.Optional[str]
    dhcp_relay: typing.Optional[str]
    ipv6_ra_configs: typing.Dict[str, str]
    _uuid: str
    _version: str


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
    external_ids: typing.Dict[str, str]
    options: typing.Dict[str, str]
    bfd: typing.Optional[str]
    ip_prefix: str
    route_table: str
    nexthop: str
    output_port: typing.Optional[str]
    policy: typing.Optional[typing.Literal["dst-ip", "src-ip"]]
    _uuid: str
    _version: str


class LogicalSwitchColumns:
    name: str
    qos_rules: typing.Set[str]
    external_ids: typing.Dict[str, str]
    other_config: typing.Dict[str, str]
    dns_records: typing.Set[str]
    ports: typing.Set[str]
    load_balancer: typing.Set[str]
    load_balancer_group: typing.Set[str]
    forwarding_groups: typing.Set[str]
    copp: typing.Optional[str]
    acls: typing.Set[str]
    _uuid: str
    _version: str


class LogicalSwitchPortColumns:
    name: str
    ha_chassis_group: typing.Optional[str]
    options: typing.Dict[str, str]
    parent_name: typing.Optional[str]
    enabled: typing.Optional[bool]
    type: str
    dhcpv6_options: typing.Optional[str]
    peer: typing.Optional[str]
    addresses: typing.Set[str]
    tag: typing.Optional[int]
    up: typing.Optional[bool]
    external_ids: typing.Dict[str, str]
    tag_request: typing.Optional[int]
    port_security: typing.Set[str]
    dhcpv4_options: typing.Optional[str]
    mirror_rules: typing.Set[str]
    dynamic_addresses: typing.Optional[str]
    _uuid: str
    _version: str


class MeterColumns:
    name: str
    unit: typing.Literal["kbps", "pktps"]
    fair: typing.Optional[bool]
    external_ids: typing.Dict[str, str]
    bands: typing.Set[str]
    _uuid: str
    _version: str


class MeterBandColumns:
    action: typing.Literal["drop"]
    rate: int
    external_ids: typing.Dict[str, str]
    burst_size: int
    _uuid: str
    _version: str


class MirrorColumns:
    filter: typing.Literal["both", "from-lport", "to-lport"]
    name: str
    sink: str
    external_ids: typing.Dict[str, str]
    index: int
    type: typing.Literal["erspan", "gre", "local"]
    _uuid: str
    _version: str


class NATColumns:
    gateway_port: typing.Optional[str]
    priority: int
    external_port_range: str
    logical_port: typing.Optional[str]
    options: typing.Dict[str, str]
    exempted_ext_ips: typing.Optional[str]
    external_ids: typing.Dict[str, str]
    allowed_ext_ips: typing.Optional[str]
    type: typing.Literal["dnat", "dnat_and_snat", "snat"]
    external_ip: str
    match: str
    external_mac: typing.Optional[str]
    logical_ip: str
    _uuid: str
    _version: str


class NBGlobalColumns:
    sb_cfg_timestamp: int
    name: str
    hv_cfg: int
    nb_cfg: int
    sb_cfg: int
    external_ids: typing.Dict[str, str]
    options: typing.Dict[str, str]
    ssl: typing.Optional[str]
    ipsec: bool
    hv_cfg_timestamp: int
    connections: typing.Set[str]
    nb_cfg_timestamp: int
    _uuid: str
    _version: str


class PortGroupColumns:
    name: str
    ports: typing.Set[str]
    external_ids: typing.Dict[str, str]
    acls: typing.Set[str]
    _uuid: str
    _version: str


class QoSColumns:
    action: typing.Dict[typing.Literal["dscp", "mark"], int]
    match: str
    bandwidth: typing.Dict[typing.Literal["burst", "rate"], int]
    priority: int
    direction: typing.Literal["from-lport", "to-lport"]
    external_ids: typing.Dict[str, str]
    _uuid: str
    _version: str


class SSLColumns:
    certificate: str
    ssl_ciphers: str
    external_ids: typing.Dict[str, str]
    ssl_ciphersuites: str
    bootstrap_ca_cert: bool
    private_key: str
    ssl_protocols: str
    ca_cert: str
    _uuid: str
    _version: str


class SampleColumns:
    collectors: typing.Set[str]
    metadata: int
    _uuid: str
    _version: str


class SampleCollectorColumns:
    name: str
    id: int
    set_id: int
    external_ids: typing.Dict[str, str]
    probability: int
    _uuid: str
    _version: str


class SamplingAppColumns:
    id: int
    external_ids: typing.Dict[str, str]
    type: typing.Literal["acl-est", "acl-new", "drop"]
    _uuid: str
    _version: str


class StaticMACBindingColumns:
    ip: str
    logical_port: str
    mac: str
    override_dynamic_mac: bool
    _uuid: str
    _version: str
