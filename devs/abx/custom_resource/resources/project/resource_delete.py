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
    
    # delete resource
    resource = vra.get('/iaas/api/projects/' + inputs['id'])
    resource['zoneAssignmentConfigurations'] = []
    vra.patch('/iaas/api/projects/' + inputs['id'], resource)
    vra.delete('/iaas/api/projects/' + inputs['id'])
    
    # publish resource
    return {}
# __ABX_IMPLEMENTATIONS_END__
