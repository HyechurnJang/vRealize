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
    if 'name' not in inputs or not inputs['name']: raise Exception('name property must be required') # Required
    if 'description' not in inputs: inputs['description'] = '' # Optional Init
    if 'sharedResources' not in inputs: inputs['sharedResources'] = True # Optional Init
    if 'administrators' not in inputs: inputs['administrators'] = [] # Optional Init
    if 'members' not in inputs: inputs['members'] = [] # Optional Init
    if 'viewers' not in inputs: inputs['viewers'] = [] # Optional Init
    if 'zones' not in inputs: inputs['zones'] = [] # Optional Init
    if 'placementPolicy' not in inputs or not inputs['placementPolicy']: inputs['placementPolicy'] = 'default' # Optional Init
    if 'customProperties' not in inputs: inputs['customProperties'] = {} # Optional Init
    if 'machineNamingTemplate' not in inputs: inputs['machineNamingTemplate'] = '' # Optional Init
    if 'operationTimeout' not in inputs: inputs['operationTimeout'] = 0 # Optional Init
    
    # create resource
    resource = vra.post('/iaas/api/projects', {
        'name': inputs['name'],
        'description': inputs['description'],
        'sharedResources': inputs['sharedResources'],
        'administrators': [{'type': 'user', 'email': account} for account in inputs['administrators']],
        'members': [{'type': 'user', 'email': account} for account in inputs['members']],
        'viewers': [{'type': 'user', 'email': account} for account in inputs['viewers']],
        'zoneAssignmentConfigurations': [{'zoneId': zoneId} for zoneId in inputs['zones']],
        'placementPolicy': inputs['placementPolicy'].upper(),
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
