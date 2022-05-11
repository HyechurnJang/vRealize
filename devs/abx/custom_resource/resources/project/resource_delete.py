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
    deployments = vra.get('/deployment/api/deployments?projects={}'.format(inputs['id']))['content']
    deploymentIds = []
    for deployment in deployments:
        deploymentIds.append(deployment['id'])
        vra.delete('/deployment/api/deployments/{}'.format(deployment['id']))
    if deploymentIds:
        time.sleep(2)
        while deploymentIds:
            for deploymentId in deploymentIds:
                try: deployment = vra.get('/deployment/api/deployments/' + deploymentId)
                except:
                    deploymentIds.remove(deploymentId)
                    break
                if deployment['status'] == 'DELETE_INPROGRESS': continue
                else:
                    raise Exception('could not delete deployment : {}'.format(deploymentId))
            else: time.sleep(5)
    
    resource = vra.get('/iaas/api/projects/' + inputs['id'])
    resource['zoneAssignmentConfigurations'] = []
    vra.patch('/iaas/api/projects/' + inputs['id'], resource)
    vra.delete('/iaas/api/projects/' + inputs['id'])
    
    # publish resource
    return {}
# __ABX_IMPLEMENTATIONS_END__
