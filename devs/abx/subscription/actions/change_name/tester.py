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

inputs = {
}

#===============================================================================
# Runtime
#===============================================================================
import action

class Context:
    @classmethod
    def getSecret(cls, value): return value 
import json

if KEY_WAIT: input('press any key to start action: ')
inputs['VraManager'] = constants['VraManager']
print('INPUTS -->\n{}\n'.format(json.dumps(inputs, indent=2)))
outputs = action.handler(Context, inputs)
print('OUTPUTS -->\n{}\n'.format(json.dumps(outputs, indent=2)))
