# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

#===============================================================================
# Test Config
#===============================================================================
inputs = {
    'vraHostname': 'vra_hostname_or_ip_here',
    'vraUsername': 'username_here',
    'vraPassword': 'password_here',
    'vraProject': 'project_here',
}

#===============================================================================
# Runtime
#===============================================================================
import json
import importlib
installer = importlib.import_module('dist.latest')

print('INPUTS -->\n{}\n'.format(json.dumps(inputs, indent=2)))
outputs = installer.handler(None, inputs)
print('OUTPUTS -->\n{}\n'.format(json.dumps(outputs, indent=2)))
