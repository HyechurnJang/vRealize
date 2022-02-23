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
import base64

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # set default values
    if 'instances' not in inputs: inputs['instances'] = []
    if 'osType' not in inputs or not inputs['osType'] or inputs['osType'] not in ['linux', 'windows']: raise Exception('osType property must be one of linux or windows') # Required
    if 'username' not in inputs or not inputs['username']: raise Exception('username property must be required') # Required
    if 'password' not in inputs or not inputs['password']: raise Exception('password property must be required') # Required
    if 'install' not in inputs: inputs['install'] = ''
    if 'configure' not in inputs: inputs['configure'] = ''
    if 'destroy' not in inputs: inputs['destroy'] = ''
    
    id = inputs['id']
    instances = inputs['instances']
    targets = inputs['targets']
    osType = inputs['osType']
    username = inputs['username']
    password = context.getSecret(inputs['password'])
    destroy = inputs['destroy']
    
    if destroy:
        delimeter = '__VRA_EXEC_DELIMETER__'
        if osType == 'linux':
            scripts = 'Output=/tmp/' + id + '.out\nexec 2>/tmp/' + id + '.err\n' + destroy
            scripts = base64.b64encode(scripts.encode('utf-8')).decode('utf-8')
            postScripts = 'echo "' + delimeter + '"\ncat /tmp/' + id + '.err | sed "s/^[/\\.].*' + id + '.sh: //g" 2>/dev/null\necho "' + delimeter + '"\ncat /tmp/' + id + '.out 2>/dev/null\nrm -rf /tmp/' + id + '.* 2>&1>/dev/null\n'
            runScripts = 'echo "' + scripts + '" | base64 -d | tee /tmp/' + id + '.sh >/dev/null\nchmod 755 /tmp/' + id + '.sh 2>&1>/dev/null\n/tmp/' + id + '.sh\n' + postScripts
        elif osType == 'windows':
            scripts = destroy
            runScripts = scripts
        
        # delete resource
        executions = {}
        executionIds = []
        for instance in instances:
            req = {
                'async-execution': True,
                'parameters': [{
                    'name': 'instance',
                    'type': 'string',
                    'value': {'string': {'value': instance}}
                },{
                    'name': 'username',
                    'type': 'string',
                    'value': {'string': {'value': username}}
                },{
                    'name': 'password',
                    'type': 'string',
                    'value': {'string': {'value': password}}
                },{
                    'name': 'scripts',
                    'type': 'string',
                    'value': {'string': {'value': runScripts}}
                }]
            }
            res = vra.post('/vco/api/actions/fc35fa64-13ec-4fa1-8273-5d1d963521ef/executions', req);
            executions[res['execution-id']] = instance
            executionIds.append(res['execution-id'])
        executionCount = len(executionIds)
        
        completedIds = []
        executionOuts = {}
        for i in range(0, 180):
            for executionId in executionIds:
                if executionId not in completedIds:
                    res = vra.get('/vco/api/actions/runs/' + executionId)
                    state = res['state']
                    if state == 'completed':
                        completedIds.append(executionId)
                        value = res['value'][res['type']]['value']
                        value = value.split(delimeter)
                        log = value[0]
                        err = value[1]
                        out = value[2]
                        executionOuts[executionId] = out
                        print('<destroy instance="{}">\n<log>{}</log>\n<err>{}</err>\n<out>{}</out>\n</destroy>'.format(executions[executionId], log, err, out))
                    elif state == 'failed': raise Exception(res['error'])
            if executionCount == len(completedIds): break
            time.sleep(5)
        else: raise Exception('scripts timeout')
        
        if executionCount == 1: consoleOutputs = executionOuts[executionIds[0]]
        elif executionCount > 1: consoleOutputs = [executionOuts[executionId] for executionId in executionIds]
        else: consoleOutputs = ''
    else: consoleOutputs = ''
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['id'] = id
    outputs['outputs'] = consoleOutputs
    outputs['targets'] = instances
    return outputs
# __ABX_IMPLEMENTATIONS_END__
