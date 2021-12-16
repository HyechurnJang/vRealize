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
    
    # update resource
    deploymentId = inputs['id']
    vra.post('/deployment/api/deployments/{}/requests'.format(deploymentId), {
        'actionId': 'Deployment.Update',
        'inputs': inputs['inputs'] if 'inputs' in inputs else {}
    })
    
    while True:
        time.sleep(5)
        resource = vra.get('/deployment/api/deployments/' + deploymentId)
        if resource['status'] == 'UPDATE_SUCCESSFUL': break
        elif resource['status'] == 'UPDATE_INPROGRESS': continue
        else:
            vra.delete('/deployment/api/deployments/' + deploymentId)
            raise Exception('could not update deployment : {} : {}'.format(inputs['name'], resource['status']))
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    return outputs
# __ABX_IMPLEMENTATIONS_END__
