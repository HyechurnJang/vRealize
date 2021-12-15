# -*- coding: utf-8 -*-
'''
Created on 2021. 11. 18.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

from pygics import rest, server, Lock, HttpResponseType
import datetime
import requests
import json
import sys
import re

PROXY_LISTEN_PORT = 18080
VRA_URL = 'https://vra.vmkloud.com'
VRA_USERNAME = ''
VRA_PASSWORD = ''
PROJECT_ID = '2968f87f-20b3-4d8f-bda1-f30f078a5132'
CATALOG_ID = '28d1717a-675c-3acd-9627-6e68131e1daa'
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

DEPLOYMENT_URL = '{}/deployment/api/deployments?search="TAS on AWS"'.format(VRA_URL)
CATALOG_URL = '{}/catalog/api/items/{}/request'.format(VRA_URL, CATALOG_ID)
LOCK = Lock()

def getToken():
    res = requests.post(VRA_URL + '/csp/gateway/am/api/login?access_token', headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }, json={
        'username': VRA_USERNAME,
        'password': VRA_PASSWORD
    }, verify=False)
    print(res.text)
    res.raise_for_status()
    refreshToken = res.json()['refresh_token']
    res = requests.post(VRA_URL + '/iaas/api/login', headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }, json={
        'refreshToken': refreshToken
    }, verify=False)
    print(res.text)
    res.raise_for_status()
    HEADERS['Authorization'] = 'Bearer ' + res.json()['token']
try:
    getToken()
except:
    print('! Error: check VRA_URL, VRA_USERNAME and VRA_PASSWORD')
    sys.exit(1)

def sendRequest(command, waitToStable, app):
    if not command: raise Exception('! Error: command must be required')
    if not waitToStable: waitToStable = '0'
    if not app: app = 'true'
    LOCK.on()
    for i in range(0, 3):
        try:
            content = requests.get(DEPLOYMENT_URL, headers=HEADERS, verify=False).json()['content']
            for deployment in content:
                if deployment['status'] == 'CREATE_INPROGRESS':
                    LOCK.off()
                    print('+ Info: already exist in-progress pipeline')
                    return 'OK'
            payload = {
                'projectId': PROJECT_ID,
                'deploymentName': 'TAS on AWS : {} [{}]'.format(command, datetime.datetime.now()),
                'inputs': {
                    'command': command,
                    'waitToStable': waitToStable,
                    'app': app
                }
            }
            res = requests.post(CATALOG_URL, headers=HEADERS, json=payload, verify=False)
            res.raise_for_status()
            print('+ Info: send request ok with status_code {} in iter count {}'.format(res.status_code, i))
            break
        except Exception as e: getToken()
    else:
        LOCK.off()
        raise Exception('! Error: could not send request to vrealize automation')
    LOCK.off()
    return 'OK'    
    
@rest('GET', '/request')
def vra_get_request(req, command, waitToStable='0', app='true'):
    return sendRequest(command, waitToStable, app)

@rest('POST', '/request')
def vra_post_request(req, command, waitToStable='0', app='true'):
    return sendRequest(command, waitToStable, app)

# @rest('POST', '/request')
# def vra_request(req):
#     return sendRequest(req.data['command'], req.data['waitToStable'] if 'waitToStable' in req.data else '0', req.data['app'] if 'app' in req.data else 'true')

#===============================================================================
# Main Server
#===============================================================================
if __name__ == '__main__':
    print('Start Proxy Server')
    server('0.0.0.0', PROXY_LISTEN_PORT)
