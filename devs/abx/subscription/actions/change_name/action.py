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
_NEWLINE_ = '\n'

# __ABX_IMPLEMENTATIONS_START__
#===============================================================================
# ABX Code Implementations                                                     #
#===============================================================================
# Import Libraries Here
import json

# Implement Handler Here
def handler(context, inputs):
    # set common values
    customProperties = inputs['customProperties']
    if 'countName' not in customProperties: return {}
    countName = customProperties['countName']
    try: countName = json.loads(countName)
    except: raise Exception('countName property must be required object type')
    if 'name' not in countName or not countName['name']: return {}
    name = countName['name']
    if 'zFill' not in countName and not countName['zFill']: zFill = 1
    else: zFill = int(countName['zFill'])
    if 'delimiter' not in countName and not countName['delimiter']: delimiter = ''
    else: delimiter = countName['delimiter']
    deploymentId = inputs['deploymentId']
    resourceId = inputs['resourceIds'][0]
    
    vra = VraManager(context, inputs)
    
    # action start
    count = []
    for resource in vra.get('/deployment/api/deployments/{}/resources'.format(deploymentId))['content']:
        properties = resource['properties']
        if resourceId in properties['resourceDescLink']:
            count.append(int(properties['countIndex']) + 1)
    
    resourceNames = []
    index = 0
    for resourceName in inputs['resourceNames']:
        while True:
            index = index + 1
            if index not in count:
                resourceNames.append('{}{}{}'.format(name, delimiter, str(index).zfill(zFill)))
                break
    return {'resourceNames': resourceNames}
# __ABX_IMPLEMENTATIONS_END__
