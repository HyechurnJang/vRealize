# -*- coding: utf-8 -*-
'''
Created on 2021. 11. 18.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

from pygics import rest, server, Lock, HttpResponseType

import uuid

DATA = {}

@rest('POST', '/external/resource')
def create_external_resource(req):
    if 'name' not in req.data: raise Exception('name is required')
    id = str(uuid.uuid4())
    data = {
        'id': id,
        'name': req.data['name'],
        'desc': 'dummy data'
    }
    DATA[id] = data
    return data 

@rest('GET', '/external/resource')
def read_external_resource(req, id=''):
    if id: return DATA[id]
    return DATA

@rest('PUT', '/external/resource')
def update_external_resource(req, id):
    data = DATA[id]
    if 'name' in req.data: data['name'] = req.data['name']
    if 'desc' in req.data: data['description'] = req.data['description']
    return data

@rest('DELETE', '/external/resource')
def delete_external_resource(req, id):
    data = DATA.pop(id)
    return data
    
#===============================================================================
# Main Server
#===============================================================================
if __name__ == '__main__':
    server('0.0.0.0', 80)
