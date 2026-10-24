#!/bin/bash

mkdir -p /var/run/ovn /var/log/ovn

# Send all daemon logs to the container's stdout via symlinks, so `docker logs`
# shows everything. We point at /proc/1/fd/1 (PID 1's stdout) rather than
# /dev/stdout because the ovsdb-servers --detach: daemonizing redirects their
# own std streams to /dev/null, so /dev/stdout would be lost. /proc/1/fd/1
# stays the container's stdout regardless.
ln -sf /proc/1/fd/1 /var/log/ovn/ovnnb_db.log
ln -sf /proc/1/fd/1 /var/log/ovn/ovnsb_db.log
# ln -sf /proc/1/fd/1 /var/log/ovn/ovn-controller.log

# Tag each daemon's log lines with a prefix by customizing its vlog pattern
# (the default pattern, with a literal "[tag] " prepended). Both NB and SB are
# the same "ovsdb-server" program, so a literal tag is the only way to tell
# them apart. Applied at runtime via ovs-appctl, retried until the daemon's
# control socket is up.
# log_fmt='%D{%Y-%m-%dT%H:%M:%SZ}|%05N|%c|%p|%m'
log_prefix() {  # $1=ctl target  $2=tag  [$3=facility=file]  [$4=rundir]
    local target=$1 tag=$2 facility=${3:-file} rundir=${4:-/var/run/openvswitch}
    for _ in $(seq 1 50); do
        OVS_RUNDIR=$rundir ovs-appctl -t "$target" \
            vlog/set "pattern:${facility}:%D{%Y-%m-%dT%H:%M:%SZ}|${tag}|%05N|%c|%p|%m" 2>/dev/null && return 0
        sleep 0.1
    done
    echo "warning: could not set log prefix '[$tag]'" >&2
}

# the ovn northbound db is the main entrypoint so we make it listen
# to tcp
echo "Starting OVN Northbound DB"
ovsdb-server /var/lib/ovn/ovnnb_db.db \
    --unixctl=/var/run/ovn/ovnnb_db.ctl \
    --remote=ptcp:6641:0.0.0.0 \
    --remote=punix:/var/run/ovn/ovnnb_db.sock \
    --remote=db:OVN_Northbound,NB_Global,connections \
    --private-key=db:OVN_Northbound,SSL,private_key \
    --certificate=db:OVN_Northbound,SSL,certificate \
    --bootstrap-ca-cert=db:OVN_Northbound,SSL,ca_cert \
    --pidfile=/var/run/ovn/ovnnb_db.pid \
    --log-file=/var/log/ovn/ovnnb_db.log \
    --detach
log_prefix /var/run/ovn/ovnnb_db.ctl nb

# listens on tcp/6642 for remote connections and on local unix socket for local management
echo "Starting OVN Southbound DB"
ovsdb-server /var/lib/ovn/ovnsb_db.db \
    --unixctl=/var/run/ovn/ovnsb_db.ctl \
    --remote=ptcp:6642:0.0.0.0 \
    --remote=punix:/var/run/ovn/ovnsb_db.sock \
    --remote=db:OVN_Southbound,SB_Global,connections \
    --private-key=db:OVN_Southbound,SSL,private_key \
    --certificate=db:OVN_Southbound,SSL,certificate \
    --bootstrap-ca-cert=db:OVN_Southbound,SSL,ca_cert \
    --pidfile=/var/run/ovn/ovnsb_db.pid \
    --log-file=/var/log/ovn/ovnsb_db.log \
    --detach
log_prefix /var/run/ovn/ovnsb_db.ctl sb

ovn-nbctl --no-wait init
ovn-sbctl init

# DON'T START OPENVSWITCH/OVN_CONTROLLER IN THIS CONTAINER. JUST MANAGE THE OVN I/O (OVN-CENTRAL)
# 
# ovn-controller does not own br-int: it only programs a local Open vSwitch.
# So Open vSwitch (conf.db server + ovs-vswitchd) must be running first.
# echo "Starting Open vSwitch"
# mkdir -p /var/run/openvswitch /etc/openvswitch /var/log/openvswitch
# ln -sf /proc/1/fd/1 /var/log/openvswitch/ovsdb-server.log
# ln -sf /proc/1/fd/1 /var/log/openvswitch/ovs-vswitchd.log
# [ -f /etc/openvswitch/conf.db ] || \
#     ovsdb-tool create /etc/openvswitch/conf.db /usr/share/openvswitch/vswitch.ovsschema
# 
# ovsdb-server /etc/openvswitch/conf.db \
#     --remote=punix:/var/run/openvswitch/db.sock \
#     --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
#     --pidfile=/var/run/openvswitch/ovsdb-server.pid \
#     --log-file=/var/log/openvswitch/ovsdb-server.log \
#     --detach
# log_prefix ovsdb-server ovs-db
# # create the Open_vSwitch root row before ovs-vswitchd / ovs-vsctl set need it
# ovs-vsctl --no-wait init
# 
# ovs-vswitchd \
#     --pidfile=/var/run/openvswitch/ovs-vswitchd.pid \
#     --log-file=/var/log/openvswitch/ovs-vswitchd.log \
#     --detach
# log_prefix ovs-vswitchd vswitchd
# 
# tell ovn-controller how to reach the Southbound DB and how to encapsulate.
# datapath_type=netdev: containers usually lack the kernel OVS datapath module.
# encap_ip=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')
# ovs-vsctl set open . \
#     external_ids:ovn-remote=unix:/var/run/ovn/ovnsb_db.sock \
#     external_ids:ovn-encap-type=geneve \
#     external_ids:ovn-encap-ip="${encap_ip:-127.0.0.1}" \
#     external_ids:system-id=chassis-1 \
#     external_ids:ovn-bridge-datapath-type=netdev
# 
# echo "Starting OVN local controller"
# ovn-ctl start_controller
# log_prefix ovn-controller controller file /var/run/ovn

echo "Running ovn-northd process"
# run in the foreground and log to the console (stderr) at info level so the
# output is captured by `docker logs`. -vconsole:info raises the console sink
# from its default (emer). exec makes northd the container's main process for
# clean signal handling on `docker stop`.
# northd logs to the console, so prefix its console pattern; do it from a
# background subshell since `exec` replaces this shell with northd.
( log_prefix ovn-northd northd console /var/run/ovn ) &
exec ovn-northd --pidfile -vconsole:info
