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

PROXY_LISTEN_PORT = 8080
VRA_HOSTNAME = 'vra.example.com'
VRA_USERNAME = ''
VRA_PASSWORD = ''
VRA_URL = 'https://' + VRA_HOSTNAME
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

LOCK = Lock()

def getToken():
    res = requests.post(VRA_URL + '/csp/gateway/am/api/login?access_token', headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }, json={
        'username': VRA_USERNAME,
        'password': VRA_PASSWORD
    }, verify=False)
    res.raise_for_status()
    refreshToken = res.json()['refresh_token']
    res = requests.post(VRA_URL + '/iaas/api/login', headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }, json={
        'refreshToken': refreshToken
    }, verify=False)
    res.raise_for_status()
    HEADERS['Authorization'] = 'Bearer ' + res.json()['token']
    
try:
    getToken()
except:
    print('! Error: check VRA_URL, VRA_USERNAME and VRA_PASSWORD')
    sys.exit(1)

@rest('POST', '/scale')
def vra_scale_request(req):
    try: command = req.data['command']
    except: return HttpResponseType.BadRequest()
    if command not in ['in', 'out']: return HttpResponseType.BadRequest()
    try: name = req.data['name']
    except: return HttpResponseType.BadRequest()
    nameEnc = name.replace(' ', '%20').replace('$', '%24').replace("'", '%27').replace('[', '%5B').replace(']', '%5D')
    try: counter = req.data['counter']
    except: return HttpResponseType.BadRequest()
    try: quantity = int(req.data['quantity'])
    except: return HttpResponseType.BadRequest()
    absolute = req.data['absolute'] if 'absolute' in req.data else 'false'
    absolute = absolute.lower()
    if absolute not in ['true', 'false']: return HttpResponseType.BadRequest()
    
    print('command : {}'.format(command))
    print('name : {} -enc-> {}'.format(name, nameEnc))
    print('counter : {}'.format(counter))
    print('quantity : {}'.format(quantity))
    print('absolute : {}'.format(absolute))

    for i in range(0, 3):
        try:
            res = requests.get('{}/deployment/api/deployments?search="{}"'.format(VRA_URL, nameEnc), headers=HEADERS, verify=False)
            res.raise_for_status()
            deployment = res.json()
            totalElements = deployment['totalElements']
            if totalElements == 0:
                print('could not find deployment : {}'.format(name))
                return HttpResponseType.ServerError()
            elif totalElements > 1:
                print('retrieved deployment are more than 2 : {}'.format(name))
                return HttpResponseType.ServerError()
            deployment = deployment['content'][0]
            if 'SUCCESSFUL' not in deployment['status']:
                print('deployment is now running update : {}'.format(name))
                return 'OK'
            try: count = deployment['inputs'][counter]
            except Exception as e:
                print('error could not find counter({}) at deployment({})'.format(counter, name))
                return HttpResponseType.BadRequest()
            if absolute == 'true': count = quantity
            else:
                if command == 'in':
                    count = count - quantity
                    if count < 1: count = 1
                else:
                    count = count + quantity
            res = requests.post('{}/deployment/api/deployments/{}/requests'.format(VRA_URL, deployment['id']), headers=HEADERS, verify=False, json={
                'actionId': 'Deployment.Update',
                'inputs': { counter: count }
            })
            res.raise_for_status()
            return 'OK'
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                LOCK.on()
                try: getToken()
                except: print('could not connect vrealize automation : {}'.format(str(e)))
                LOCK.off()
            elif e.response.status_code == 409: return 'Already in Scale Status'
            else: return str(e)
    else:
        return HttpResponseType.ServerError()
    
#===============================================================================
# Main Server
#===============================================================================
if __name__ == '__main__':
    print('Start Scale Proxy Server')
    server('0.0.0.0', PROXY_LISTEN_PORT)
