#!/bin/bash

FULL_PATH=$(realpath $0)
CURRENT_PATH=$(dirname $FULL_PATH)
ANSIBLE_PATH="/etc/ansible"

apt install -y ansible sshpass
if [ ! -f "$ANSIBLE_PATH/ansible.cfg.vra.bak" ]; then
mv $ANSIBLE_PATH/ansible.cfg $ANSIBLE_PATH/ansible.cfg.vra.bak
ln -s $CURRENT_PATH/ansible.cfg $ANSIBLE_PATH/ansible.cfg
ln -s $CURRENT_PATH/password $ANSIBLE_PATH/password
ln -s $CURRENT_PATH/playbooks /playbooks
fi
