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
    pipelineId = inputs['id']
    try: executionLink = vra.post('/codestream/api/pipelines/{}/executions'.format(pipelineId), {'input': {'method': 'delete'}})['executionLink']
    except: pass
    
    for _ in range(0, 300):
        execution = vra.get(executionLink)
        if execution['status'] == 'COMPLETED': break
        elif execution['status'] == 'FAILED': break
        time.sleep(3)
    
    if not inputs['persistence']:
        try: vra.delete('/codestream/api/pipelines/' + inputs['id'])
        except: pass
    
    # publish null resource
    return {}
# __ABX_IMPLEMENTATIONS_END__
