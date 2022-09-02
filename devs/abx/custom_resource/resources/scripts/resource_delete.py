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
import json
import base64

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # set default values
    id = inputs['id']
    instances = inputs['instances'] if 'instances' in inputs and inputs['instances'] else [] 
    if 'osType' not in inputs or not inputs['osType'] or inputs['osType'] not in ['linux', 'windows']: raise Exception('osType property must be one of linux or windows') # Required
    osType = inputs['osType']
    if 'username' not in inputs or not inputs['username']: raise Exception('username property must be required') # Required
    username = inputs['username']
    if 'password' not in inputs or not inputs['password']: raise Exception('password property must be required') # Required
    password = inputs['password'] = context.getSecret(inputs['password'])
    destroy = inputs['destroy'] if 'destroy' in inputs and inputs['destroy'] else ''
    delimeter = '__VRA_EXEC_DELIMETER__'
    
    print('[INFO] Update Scripts Description')
    print('properties.instances\n{}\n'.format(instances))
    print('properties.osType\n{}\n'.format(osType))
    print('properties.username\n{}\n'.format(username))
    print('properties.password\n{}\n'.format(password))
    print('properties.destroy\n{}\n'.format(destroy))
    
    if destroy:
        if osType == 'linux':
            scripts = '''# Scripts
exec 1>/tmp/{id}.stdout
exec 2>/tmp/{id}.stderr
output=/tmp/{id}.output
{destroy}
'''.format(id=id, destroy=destroy)
            scripts = base64.b64encode(scripts.encode('utf-8')).decode('utf-8')
            runScripts = '''# Scripts
rm -rf /tmp/{id}.* 2>&1>/dev/null
echo "{scripts}" | base64 -d | tee /tmp/{id}.sh >/dev/null
chmod 755 /tmp/{id}.sh 2>&1>/dev/null
/tmp/{id}.sh
cat /tmp/{id}.stdout 2>/dev/null
echo "{delimeter}"
cat /tmp/{id}.stderr | sed "s/^[/\\.].*{id}.sh: //g" 2>/dev/null
echo "{delimeter}"
cat /tmp/{id}.output 2>/dev/null
'''.format(id=id, scripts=scripts, delimeter=delimeter)
        elif osType == 'windows':
            runScripts = destroy
        
        # create resource
        executions = {}
        executionIds = []
        for instance in instances:
            res = vra.post('/vco/api/workflows/8368da88-53ff-4285-af9b-c8fcea894901/executions', {
                'parameters': [{
                    'name': 'vmLink',
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
            })
            executions[res['id']] = instance
            executionIds.append(res['id'])
        executionCount = len(executionIds)
        
        completedIds = []
        executionOuts = {}
        for _ in range(0, 300):
            for executionId in executionIds:
                if executionId not in completedIds:
                    res = vra.get('/vco/api/workflows/8368da88-53ff-4285-af9b-c8fcea894901/executions/' + executionId + '/state')
                    state = res['value']
                    if state != 'running':
                        res = vra.get('/vco/api/workflows/8368da88-53ff-4285-af9b-c8fcea894901/executions/' + executionId)
                        if state == 'completed':
                            completedIds.append(executionId)
                            value = res['output-parameters'][0]['value']['string']['value'].split(delimeter)
                            log = value[0]
                            err = value[1]
                            out = value[2].strip()
                            executionOuts[executionId] = out
                            print('<destroy instance="{}" resource="scripts">\n<log>{}</log>\n<err>{}</err>\n<out>{}</out>\n</destroy>'.format(executions[executionId], log, err, out))
                        elif state == 'failed': raise Exception(res['content-exception'])
            if executionCount == len(completedIds): break
            time.sleep(2)
        else: raise Exception('scripts timeout')
        
        if executionCount == 1: consoleOutputs = executionOuts[executionIds[0]]
        elif executionCount > 1: consoleOutputs = [executionOuts[executionId] for executionId in executionIds]
        else: consoleOutputs = ''
    else: consoleOutputs = ''
    
    # publish null resource
    return {}
# __ABX_IMPLEMENTATIONS_END__
