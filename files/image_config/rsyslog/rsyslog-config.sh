#!/bin/bash

PLATFORM=`sonic-cfggen -H -v DEVICE_METADATA.localhost.platform`
CHASSIS_NAME=`sonic-cfggen -d -v DEVICE_METADATA.localhost.chassis_name`
SLOT_ID=`sonic-cfggen -d -v DEVICE_METADATA.localhost.slot_id`

# Parse the device specific asic conf file, if it exists
ASIC_CONF=/usr/share/sonic/device/$PLATFORM/asic.conf
if [ -f "$ASIC_CONF" ]; then
    source $ASIC_CONF
fi

# On Multi NPU platforms we need to start  the rsyslog server on the docker0 ip address
# for the syslogs from the containers in the namespaces to work.
# on Single NPU platforms we continue to use loopback adddres

if [[ ($NUM_ASIC -gt 1) ]]; then
    udp_server_ip=$(ip -o -4 addr list docker0 | awk '{print $4}' | cut -d/ -f1)
else
    udp_server_ip=$(ip -j -4 addr list lo scope host | jq -r -M '.[0].addr_info[0].local')
fi
hostname=$(hostname)

template="\"udp_server_ip\": \"$udp_server_ip\", \"hostname\": \"$hostname\""
echo $template
if [ -n "$CHASSIS_NAME" ]; then
    template="$template, \"chassis_name_marker\": \"CHASSIS_NAME:\""
fi

if [ -n "$SLOT_ID" ]; then
    template="$template, \"slot_id_marker\": \"SLOT_ID:\""
fi

sonic-cfggen -d -t /usr/share/sonic/templates/rsyslog.conf.j2 -a "{$template}" >/etc/rsyslog.conf
systemctl restart rsyslog