# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

#===============================================================================
# Test Config
#===============================================================================
KEY_WAIT = True

constants = {
    'VraManager': {
        'hostname': 'vra_hostname_or_ip_here',
        'username': 'username_here',
        'password': 'password_here'
    }
}

createInputs = {
    'name': 'test-project'
}

updateInputs = {
    'name': 'updated-test-project'
}

#===============================================================================
# Runtime
#===============================================================================
import resource_create
import resource_read
import resource_update
import resource_delete

class Context:
    @classmethod
    def getSecret(cls, value): return value 
import json

if KEY_WAIT: input('press any key to start create: ')
createInputs['VraManager'] = constants['VraManager']
print('CREATE INPUTS -->\n{}\n'.format(json.dumps(createInputs, indent=2)))
outputs = resource_create.handler(Context, createInputs)
print('CREATE OUTPUTS -->\n{}\n'.format(json.dumps(outputs, indent=2)))

if KEY_WAIT: input('press any key to start read: ')
inputs = outputs
print('READ INPUTS -->\n{}\n'.format(json.dumps(inputs, indent=2)))
outputs = resource_read.handler(Context, inputs)
print('READ OUTPUTS -->\n{}\n'.format(json.dumps(outputs, indent=2)))

if KEY_WAIT: input('press any key to start update: ')
inputs = outputs
inputs['VraManager'] = constants['VraManager']
for k, v in updateInputs.items(): inputs[k] = v
print('UPDATE INPUTS -->\n{}\n'.format(json.dumps(inputs, indent=2)))
outputs = resource_update.handler(Context, inputs)
print('UPDATE OUTPUTS -->\n{}\n'.format(json.dumps(outputs, indent=2)))

if KEY_WAIT: input('press any key to start delete: ')
inputs = outputs
inputs['VraManager'] = constants['VraManager']
print('DELETE INPUTS -->\n{}\n'.format(json.dumps(inputs, indent=2)))
outputs = resource_delete.handler(Context, inputs)
print('DELETE OUTPUTS -->\n{}\n'.format(json.dumps(outputs, indent=2)))