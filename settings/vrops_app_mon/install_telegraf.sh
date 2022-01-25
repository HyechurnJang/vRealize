#!/bin/bash

VROPS_HOSTNAME=""
VROCP_HOSTNAME=""
VROPS_USERNAME=""
VROPS_PASSWORD=""
TELEGRAF_VERSION="telegraf_1.21.2-1_amd64.deb"

apt install -y jq
wget https://dl.influxdata.com/telegraf/releases/$TELEGRAF_VERSION -O /tmp/telegraf.deb
dpkg -i /tmp/telegraf.deb
wget --no-check-certificate https://$VROCP_HOSTNAME/downloads/salt/open_source_telegraf_monitor.sh -O /tmp/telegraf.sh
chmod 755 /tmp/telegraf.sh
TOKEN=$(curl -k -XPOST "https://$VROPS_HOSTNAME/suite-api/api/auth/token/acquire" -H "Content-Type: application/json" -H "Accept: application/json" -d "{\"username\":\"$VROPS_USERNAME\",\"authSource\":\"Local\",\"password\":\"$VROPS_PASSWORD\"}" | jq ".token" | sed "s/\"//g")
/tmp/telegraf.sh -v $VROPS_HOSTNAME -t $TOKEN -c $VROCP_HOSTNAME -d /etc/telegraf/telegraf.d -e /usr/bin/telegraf
sed -i "s/^\[\[outputs\.influxdb\]\]/#\[\[outputs\.influxdb\]\]/g" /etc/telegraf/telegraf.conf
systemctl restart telegraf
