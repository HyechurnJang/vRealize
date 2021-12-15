# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

import sys
import importlib
import manifest
sys.path.insert(0, '../../common')
_module = importlib.import_module(manifest.sdk)
for exportObject in _module.exportObjects: __builtins__[exportObject] = _module.__getattribute__(exportObject)

# __ABX_IMPLEMENTATIONS_START__
#===============================================================================
# ABX Code Implementations                                                     #
#===============================================================================
# Import Libraries Here

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # set default values
    if 'description' not in inputs: inputs['description'] = ''
    if 'sharedResources' not in inputs: inputs['sharedResources'] = True
    if 'administrators' not in inputs: inputs['administrators'] = []
    if 'members' not in inputs: inputs['members'] = []
    if 'viewers' not in inputs: inputs['viewers'] = []
    if 'zones' not in inputs: inputs['zones'] = []
    if 'placementPolicy' not in inputs: inputs['placementPolicy'] = 'DEFAULT'
    if 'customProperties' not in inputs: inputs['customProperties'] = {}
    if 'machineNamingTemplate' not in inputs: inputs['machineNamingTemplate'] = ''
    if 'operationTimeout' not in inputs: inputs['operationTimeout'] = 0
    
    # create resource
    resource = vra.post('/iaas/api/projects', {
        'name': inputs['name'],
        'description': inputs['description'],
        'sharedResources': inputs['sharedResources'],
        'administrators': [{'type': 'user', 'email': account} for account in inputs['administrators']],
        'members': [{'type': 'user', 'email': account} for account in inputs['members']],
        'viewers': [{'type': 'user', 'email': account} for account in inputs['viewers']],
        'zones': [{'zoneId': zoneId} for zoneId in inputs['zones']],
        'placementPolicy': inputs['placementPolicy'],
        'customProperties': inputs['customProperties'],
        'machineNamingTemplate': inputs['machineNamingTemplate'],
        'operationTimeout': inputs['operationTimeout']
    })
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['id'] = resource['id']
    return outputs
# __ABX_IMPLEMENTATIONS_END__
