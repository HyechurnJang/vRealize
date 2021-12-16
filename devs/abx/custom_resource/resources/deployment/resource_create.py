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
    
    # set default values
    if 'inputs' not in inputs: inputs['inputs'] = {}
    
    # get project
    for project in vra.get("/iaas/api/projects?$filter=(name eq '{}')".format(inputs['projectName']))['content']:
        if project['name'] == inputs['projectName']: break
    else: raise Exception('could not find project : {}'.format(inputs['projectName']))
    
    # create resource
    if inputs['itemType'] == 'blueprint':
        for blueprint in vra.get('/blueprint/api/blueprints?search={}'.format(inputs['itemName']))['content']:
            if blueprint['name'] == inputs['itemName']: break
        else: raise Exception('could not find blueprint : {}'.format(inputs['itemName']))
        deploymentId = vra.post('/blueprint/api/blueprint-requests', {
            'projectId': project['id'],
            'deploymentName': inputs['name'],
            'blueprintId': blueprint['id'],
            'inputs': inputs['inputs']
        })['deploymentId']
    elif inputs['itemType'] == 'catalog':
        for catalog in vra.get('/catalog/api/items?search={}'.format(inputs['itemName']))['content']:
            if catalog['name'] == inputs['itemName']: break
        else: raise Exception('could not find catalog : {}'.format(inputs['itemName']))
        deploymentId = vra.post('/catalog/api/items/{}/request'.format(catalog['id']), {
            'projectId': project['id'],
            'deploymentName': inputs['name'],
            'inputs': inputs['inputs']
        })['deploymentId']
    else: raise Exception('itemType must be set "blueprint" or "catalog"')
    
    while True:
        time.sleep(5)
        resource = vra.get('/deployment/api/deployments/' + deploymentId)
        if resource['status'] == 'CREATE_SUCCESSFUL': break
        elif resource['status'] == 'CREATE_INPROGRESS': continue
        else:
            vra.delete('/deployment/api/deployments/' + deploymentId)
            raise Exception('could not deploy item : {} : {}'.format(inputs['itemName'], resource['status']))
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['id'] = resource['id']
    return outputs
# __ABX_IMPLEMENTATIONS_END__
