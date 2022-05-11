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
    address = inputs['address']
    port = inputs['port'] if 'port' in inputs and inputs['port'] else 22
    sync = inputs['sync'] if 'sync' in inputs and inputs['sync'] in [True, False] else True
    executionId = inputs['executionId'] if 'executionId' in inputs and inputs['executionId'] else ''
        
    if not sync and executionId:
        delimeter = '__VRA_EXEC_DELIMETER__'
        res = vra.get('/vco/api/actions/runs/' + executionId)
        state = res['state']
        if state == 'completed':
            value = res['value'][res['type']]['value'].split(delimeter)
            log = value[0]
            error = value[1]
            output = value[2].strip()
            print('<sync resource="ssh" address="{}" port="{}">\n<log>{}</log>\n<error>{}</error>\n<output>{}</output>\n</sync>'.format(address, port, log, error, output))
            inputs['output'] = output
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    inputs['password'] = context.getSecret(inputs['password'])
    return outputs
# __ABX_IMPLEMENTATIONS_END__
