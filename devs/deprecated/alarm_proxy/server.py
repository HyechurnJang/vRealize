# -*- coding: utf-8 -*-
'''
Created on 2021. 11. 18.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

from pygics import rest, server
import requests
import json
import re

DEBUG=True
MOCK=True
TOKEN = ''
PROXY_LISTEN_PORT = 80

OPSGENIE_URL = 'https://api/opsgenie.com/v2/alerts'
OPSGENIE_HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'GenieKey ' + TOKEN
}

#===============================================================================
# {
#     "name": "Alert Name",
#     "timestamp": "Alert Time",
#     "host": "Alert Target",
#     "detail": "Messages",
#     "priority": "etc P1"
# }
#===============================================================================
def sendOpsGenieAlert(name, timestamp, host, detail, priority='P1', **kwargs):
    payload = {
        'message': 'vRealize Alert - {}'.format(name),
        'description': '{} / {} / {}'.format(timestamp, host, detail),
        'alias': '경고발생: {}'.format(host),
        'entity': '증상: {}'.format(name),
        'priority': priority
    }
    if DEBUG: print('Payload\n{}\n'.format(json.dumps(payload, indent=2)))
    if not MOCK:
        try:
            requests.post(OPSGENIE_URL, headers=OPSGENIE_HEADERS, json={
                'message': 'vRealize Alert - {}'.format(name),
                'description': '{} / {} / {}'.format(timestamp, host, detail),
                'alias': '경고발생: {}'.format(host),
                'entity': '증상: {}'.format(name),
                'priority': priority
            }, verify=False)
        except Exception as e:
            print('! Could not send OpsGenie Alert : {}'.format(str(e)))
        else:
            print('+ OpsGenie Alert is sent')

#===============================================================================
# vRLI Payload Template
# {
#     "alert_type": "${AlertType}",
#     "alert_name": "${AlertName}",
#     "search_period": "${SearchPeriod}",
#     "hit_oeprator": "${HitOperator}",
#     "triggered_at": "${TriggeredAt}",
#     "messages": "'${messages}'"
# }
#===============================================================================
LI_REGEX = r"\"name\":\"hostname\",\"content\":\"(?P<hostname>[\.\w-]+)"
def parseLItoPayload(data):
    name = data['alert_name']
    tstamp = data['triggered_at']
    messages = data['messages']
    hostnames = re.findall(LI_REGEX, messages)
    hosts = []
    for hostname in hostnames:
        if hostname not in hosts: hosts.append(hostname)
    print('Name : {}\nTimeStamp : {}\nMessages\n{}\nHostnames : {}\nHosts : {}\n'.format(name, tstamp, messages, hostnames, hosts))

#===============================================================================
# vROps Proxy Endpoints
#===============================================================================
@rest('POST', '/vrops/alerts')
def vrops_alerts(req):
    sendOpsGenieAlert('vROps Alert', req.data['alertTime'], req.data['alertHost'], req.data['alert'])

#===============================================================================
# vRLI Proxy Endpoints
#===============================================================================
@rest('POST', '/vrli/abnormal_access')
def vrli_abnormal_access(req):
    parseLItoPayload(req.data)
    # sendOpsGenieAlert(**req.data)

#===============================================================================
# Main Server
#===============================================================================
if __name__ == '__main__':
    print('Start Proxy Server')
    server('0.0.0.0', PROXY_LISTEN_PORT)
