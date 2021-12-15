# -*- coding: utf-8 -*-
'''
Created on 2021. 11. 18.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

from pygics import rest, server
import json
import re

PROXY_LISTEN_PORT = 80

LI_REGEX = r"\"name\":\"hostname\",\"content\":\"(?P<hostname>[\.\w-]+)"
def parseLItoPayload(data):
    name = data['alert_name']
    tstamp = data['triggered_at']
    messages = data['messages']
    hostnames = re.findall(LI_REGEX, messages)
    hosts = []
    for hostname in hostnames:
        if hostname not in hosts: hosts.append(hostname)
    print('Name : {}\nTimeStamp : {}\nHosts : {}\n'.format(name, tstamp, hosts))

@rest('POST', '/vrli/abnormal_access')
def vrli_abnormal_access(req):
    parseLItoPayload(req.data)
    return 'OK'

if __name__ == '__main__':
    print('Start Proxy Server')
    server('0.0.0.0', PROXY_LISTEN_PORT)