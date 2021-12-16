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
import time

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # delete resource
    deploymentId = inputs['id']
    vra.delete('/deployment/api/deployments/' + deploymentId)
    
    while True:
        time.sleep(5)
        try: resource = vra.get('/deployment/api/deployments/' + deploymentId)
        except: break
        if resource['status'] == 'DELETE_INPROGRESS': continue
        else:
            raise Exception('could not delete deployment : {} : {}'.format(inputs['name'], resource['status']))
    
    # publish null resource
    return {}
# __ABX_IMPLEMENTATIONS_END__
