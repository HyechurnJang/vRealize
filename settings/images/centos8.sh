#!/bin/bash
# must be run as root
# must be run with image "CentOS-8.X.-.iso" with minimal install
# must be prepared /etc/selinux/config > SELINUX=disabled > reboot

DNS="168.126.63.1"			# set your dns server
NTP="time.kriss.re.kr"		# set your ntp server
REPO=""						# set your repository
SSL_PUB_KEY=""				# set your master public ssh key

# 1. remove non-cloudic packages

## swap system off			# check stable way
swapoff -a
rm -rf /swap.img
sed -i '/swap/d' /etc/fstab

## remove package from yum
systemctl disable vmtoolsd
systemctl stop vmtoolsd
yum remove -y open-vm-tools

# upgrade && install basic packages
if [ -n "$REPO" ]; then
rm -rf /etc/yum.repos.d/*
cat <<EOF> /etc/yum.repos.d/vmkloud.repo
[BaseOS]
name=VMKLOUD CentOS BaseOS Repository
baseurl=http://$REPO/BaseOS/
gpgcheck=0
enabled=1

[AppStream]
name=VMKLOUD CentOS AppStream Repository
baseurl=http://$REPO/AppStream/
gpgcheck=0
enabled=1
EOF
fi
yum update -y
yum install -y net-tools bind-utils tar perl wget

# settings
## grub bootloader
sed -i 's/GRUB_TIMEOUT=5/GRUB_TIMEOUT=0/g' /etc/default/grub
grub2-mkconfig -o /boot/efi/EFI/centos/grub.cfg

## ssh
sed -i 's/#ClientAliveInterval 0/ClientAliveInterval 300/g' /etc/ssh/sshd_config
sed -i 's/#ClientAliveCountMax 3/ClientAliveCountMax 12/g' /etc/ssh/sshd_config
sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/g' /etc/ssh/sshd_config
cat <<EOF> /etc/ssh/ssh_config.d/99-cloud.conf
StrictHostKeyChecking no
UserKnownHostsFile /dev/null
EOF
mkdir -p /root/.ssh
if [ -n "$SSL_PUB_KEY" ]; then
	echo "$SSL_PUB_KEY" >> /root/.ssh/authorized_keys
	chmod 600 /root/.ssh/authorized_keys
fi
systemctl restart sshd

## system daemon
sed -i 's/#DefaultTimeoutStartSec=90s/DefaultTimeoutStartSec=10s/g' /etc/systemd/system.conf
sed -i 's/#DefaultTimeoutStopSec=90s/DefaultTimeoutStopSec=10s/g' /etc/systemd/system.conf
systemctl daemon-reload

## network & time
cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime
if [ -n "$DNS" ]; then
	sed -i "s/#DNS=/DNS=$DNS/g" /etc/systemd/resolved.conf
fi
if [ -n "$NTP" ]; then
	sed -i "s/server /#server /g" /etc/chrony.conf
	echo "server $NTP iburst" >> /etc/chrony.conf
fi

# install required packages
## vmware tools
echo "check vmware tools disconnection in vcenter"
echo "and execute installing vmware tools in guest operation menu"
echo -n "press enter to next: "; read _KEY
mount /dev/cdrom /mnt
cp /mnt/VMwareTools-* /tmp/vmtools.tar.gz
cd /tmp && tar -xzvf vmtools.tar.gz
/tmp/vmware-tools-distrib/vmware-install.pl
cd ~

## cloud-init
yum install -y cloud-init
systemctl disable cloud-init-local cloud-init cloud-config cloud-final
sed -i 's/disable_root: 1/disable_root: 0/g' /etc/cloud/cloud.cfg
sed -i 's/ssh_pwauth:   0/ssh_pwauth:   1/g' /etc/cloud/cloud.cfg
sed -i '/disable_vmware_customization: false/d' /etc/cloud/cloud.cfg
echo 'network: {config: disabled}' > /etc/cloud/cloud.cfg.d/99_network_disabled.cfg

# util for vra
VRA_INIT_SERVICE="W1VuaXRdCkRlc2NyaXB0aW9uPXZSZWFsaXplIEF1dG9tYXRpb24gSW5pdCBTZXJ2aWNlCkFmdGVyPXZtd2FyZS10b29scy5zZXJ2aWNlCgpbU2VydmljZV0KVHlwZT1vbmVzaG90CkV4ZWNTdGFydD0vdXNyL2Jpbi92cmEtaW5pdApSZW1haW5BZnRlckV4aXQ9eWVzClRpbWVvdXRTZWM9MApLaWxsTW9kZT1wcm9jZXNzClRhc2tzTWF4PWluZmluaXR5ClN0YW5kYXJkT3V0cHV0PWpvdXJuYWwrY29uc29sZQoKW0luc3RhbGxdCldhbnRlZEJ5PW11bHRpLXVzZXIudGFyZ2V0"
VRA_INIT="IyEvYmluL2Jhc2gKQ0hFQ0tfTkVUV09SS19USUNLPTEKZnVuY3Rpb24gX2NoZWNrX25ldHdvcmsgewogICAgbG9jYWwgREVWX05BTUU9YGlwIGxpbmsgfCBncmVwICJeMjoiIHwgYXdrICd7cHJpbnQgJDJ9JyB8IHNlZCAtZSAncy86Ly9nJ2AKICAgIGlmIFsgLXogIiRERVZfTkFNRSIgXTsgdGhlbiByZXR1cm4gMTsgZmkKICAgIGlmIFsgLXogImBpcCBhZGRyIHNob3cgZGV2ICRERVZfTkFNRSB8IGdyZXAgImluZXQgIiB8IGF3ayAne3ByaW50ICQyfScgfCBzZWQgLWUgJ3MvXC8uXCsvL2cnYCIgXTsgdGhlbiByZXR1cm4gMTsgZmkKICAgIHJldHVybiAwCn0KZnVuY3Rpb24gY2hlY2tfbmV0d29yayB7CiAgICB3aGlsZSB0cnVlOyBkbwogICAgICAgIF9jaGVja19uZXR3b3JrCiAgICAgICAgaWYgWyAkPyA9PSAgMCBdOyB0aGVuIGJyZWFrOyBmaQogICAgICAgIHNsZWVwICRDSEVDS19ORVRXT1JLX1RJQ0sKICAgIGRvbmUKfQpmdW5jdGlvbiBfc3RhcnRfY2xvdWRfaW5pdCB7CiAgICAvdXNyL2Jpbi9jbG91ZC1pbml0IGluaXQgLS1sb2NhbAogICAgL3Vzci9iaW4vY2xvdWQtaW5pdCBpbml0CiAgICAvdXNyL2Jpbi9jbG91ZC1pbml0IG1vZHVsZXMgLS1tb2RlPWNvbmZpZwogICAgL3Vzci9iaW4vY2xvdWQtaW5pdCBtb2R1bGVzIC0tbW9kZT1maW5hbAp9CmZ1bmN0aW9uIHN0YXJ0X2Nsb3VkX2luaXQgewogICAgY2hlY2tfbmV0d29yawogICAgX3N0YXJ0X2Nsb3VkX2luaXQgMj4mMSA+L3Zhci9sb2cvY2xvdWQtaW5pdC5sb2cgJgp9CgppZiBbIC1mIC9ldGMvdnJhLXJlYWR5IF07IHRoZW4KICAgIGlmIFsgIk9LIiAhPSAiJChjYXQgL2V0Yy92cmEtcmVhZHkpIiBdOyB0aGVuCiAgICAgICAgc3RhcnRfY2xvdWRfaW5pdAogICAgZmkKICAgIGVjaG8gIk9LIiA+IC9ldGMvdnJhLXJlYWR5CmVsc2UKICAgIHRvdWNoIC9ldGMvdnJhLXJlYWR5CmZpCg=="
VRA_READY="IyEvYmluL2Jhc2gKCiMgRW5hYmxlIHZyYS1pbml0CnN5c3RlbWN0bCBlbmFibGUgdnJhLWluaXQKIyBSZW1vdmUgdnJhLWluaXQgUGhhc2UgQ2hlY2tlcgpybSAtcmYgL2V0Yy92cmEtcmVhZHkKIyBSZW1vdmUgVWJ1bnR1IE5ldHdvcmsgRmlsZXMKcm0gLXJmIC9ldGMvbmV0d29yay9pbnRlcmZhY2VzCnJtIC1yZiAvZXRjL25ldHBsYW4vKgojIFJlbW92ZSBDZW50T1MgTmV0d29yayBGSWxlcwpybSAtcmYgL2V0Yy9zeXNjb25maWcvbmV0d29yay1zY3JpcHRzL2lmY2ZnLSoKIyBSZW1vdmUgQ2xvdWQgaW5pdCBEYXRhCnJtIC1yZiAvdmFyL2xpYi9jbG91ZC8qCiMgR2VuZXJhbCBDbGVhcmluZwovdXNyL2Jpbi9pbWFnZS1jbGVhci1wb3dlcm9mZgo="
IMG_CL_PO="IyEvYmluL2Jhc2gKCnJtIC1yZiAvdG1wLyoKcm0gLXJmIC92YXIvdG1wLyoKcm0gLXJmIC92YXIvbG9nL3Ztd2FyZS0qCnJtIC1yZiAvdmFyL2xvZy9jbG91ZC0qCmZvciBmZCBpbiAkKGZpbmQgL3Zhci9sb2cgfCBncmVwICIuZ3oiKTsgZG8gcm0gLXJmICRmZDsgZG9uZQpmb3IgZmQgaW4gJChmaW5kIC92YXIvbG9nIHwgZ3JlcCAiLnR6Iik7IGRvIHJtIC1yZiAkZmQ7IGRvbmUKZm9yIGZkIGluICQoZmluZCAvdmFyL2xvZyB8IGdyZXAgIi56aXAiKTsgZG8gcm0gLXJmICRmZDsgZG9uZQpybSAtcmYgfi8uYmFzaF9oaXN0b3J5CnBvd2Vyb2ZmCg=="
echo "$VRA_INIT_SERVICE" | base64 -d | tee /lib/systemd/system/vra-init.service > /dev/null
echo "$VRA_INIT" | base64 -d | tee /usr/bin/vra-init > /dev/null
echo "$VRA_READY" | base64 -d | tee /usr/bin/vra-ready > /dev/null
echo "$IMG_CL_PO" | base64 -d | tee /usr/bin/image-clear-poweroff > /dev/null
chmod 755 /usr/bin/vra-init /usr/bin/vra-ready /usr/bin/image-clear-poweroff
systemctl disable vra-init

# clear unusable packages
yum clean all

# finish
echo ""
echo "if want to make image to finalize"
echo "input command as followed"
echo ""
echo "...# vra-ready"
echo ""
echo "thanks"