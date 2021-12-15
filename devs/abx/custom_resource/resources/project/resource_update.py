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
    
    # retrieve resource
    resource = vra.get('/iaas/api/projects/' + inputs['id'])
    
    # update resource
    if 'name' in inputs: resource['name'] = inputs['name']
    if 'description' in inputs: resource['description'] = inputs['description']
    if 'sharedResources' in inputs: resource['sharedResources'] = inputs['sharedResources']
    if 'administrators' in inputs and inputs['administrators']: resource['administrators'] = [{'type': 'user', 'email': account} for account in inputs['administrators']]
    if 'members' in inputs and inputs['members']: resource['members'] = [{'type': 'user', 'email': account} for account in inputs['members']]
    if 'viewers' in inputs and inputs['viewers']: resource['viewers'] = [{'type': 'user', 'email': account} for account in inputs['viewers']]
    if 'zones' in inputs and inputs['zones']: resource['zoneAssignmentConfigurations'] = [{'zoneId': zoneId} for zoneId in inputs['zones']]
    if 'placementPolicy' in inputs: resource['placementPolicy'] = inputs['placementPolicy']
    if 'customProperties' in inputs: resource['customProperties'] = inputs['customProperties']
    if 'machineNamingTemplate' in inputs: resource['machineNamingTemplate'] = inputs['machineNamingTemplate']
    if 'operationTimeout' in inputs: resource['operationTimeout'] = inputs['operationTimeout']
    vra.patch('/iaas/api/projects/' + inputs['id'], resource)
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    return outputs
# __ABX_IMPLEMENTATIONS_END__
