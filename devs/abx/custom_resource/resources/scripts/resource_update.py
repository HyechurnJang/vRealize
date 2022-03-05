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
    id = inputs['id']
    targets = inputs['targets']
    instances = inputs['instances'] if 'instances' in inputs and inputs['instances'] else [] 
    if 'osType' not in inputs or not inputs['osType'] or inputs['osType'] not in ['linux', 'windows']: raise Exception('osType property must be one of linux or windows') # Required
    osType = inputs['osType']
    if 'username' not in inputs or not inputs['username']: raise Exception('username property must be required') # Required
    username = inputs['username']
    if 'password' not in inputs or not inputs['password']: raise Exception('password property must be required') # Required
    password = inputs['password'] = context.getSecret(inputs['password'])
    install = inputs['install'] if 'install' in inputs and inputs['install'] else ''
    configure = inputs['configure'] if 'configure' in inputs and inputs['configure'] else ''
    destroy = inputs['destroy'] if 'destroy' in inputs and inputs['destroy'] else ''
    delimeter = '__VRA_EXEC_DELIMETER__'
    
    print('[INFO] Update Scripts Description')
    print('properties.instances\n{}\n'.format(instances))
    print('properties.targets\n{}\n'.format(targets))
    print('properties.osType\n{}\n'.format(osType))
    print('properties.username\n{}\n'.format(username))
    print('properties.password\n{}\n'.format(password))
    print('properties.install\n{}\n'.format(install))
    print('properties.configure\n{}\n'.format(configure))
    print('properties.destroy\n{}\n'.format(destroy))
        
    deleteInstances = []
    for instance in targets:
        if instance not in instances: deleteInstances.append(instance)
    if deleteInstances and destroy:
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
        
        # delete resource
        executions = {}
        executionIds = []
        for instance in deleteInstances:
            res = vra.post('/vco/api/actions/fc35fa64-13ec-4fa1-8273-5d1d963521ef/executions', {
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
            })
            executions[res['execution-id']] = instance
            executionIds.append(res['execution-id'])
        executionCount = len(executionIds)
        
        completedIds = []
        for _ in range(0, 300):
            for executionId in executionIds:
                if executionId not in completedIds:
                    res = vra.get('/vco/api/actions/runs/' + executionId)
                    state = res['state']
                    if state == 'completed':
                        completedIds.append(executionId)
                        value = res['value'][res['type']]['value'].split(delimeter)
                        log = value[0]
                        err = value[1]
                        out = value[2].strip()
                        print('<update instance="{}" resource="scripts">\n<log>{}</log>\n<err>{}</err>\n<out>{}</out>\n</update>'.format(executions[executionId], log, err, out))
                    elif state == 'failed': raise Exception(res['error'])
            if executionCount == len(completedIds): break
            time.sleep(2)
        else: raise Exception('scripts timeout')
    
    if instances and (install or configure):
        if osType == 'linux':
            createScripts = '''# Scripts
exec 1>/tmp/{id}.stdout
exec 2>/tmp/{id}.stderr
output=/tmp/{id}.output
{install}
{configure}
'''.format(id=id, install=install, configure=configure)
            createScripts = base64.b64encode(createScripts.encode('utf-8')).decode('utf-8')
            runCreateScripts = '''# Scripts
rm -rf /tmp/{id}.* 2>&1>/dev/null
echo "{scripts}" | base64 -d | tee /tmp/{id}.sh >/dev/null
chmod 755 /tmp/{id}.sh 2>&1>/dev/null
/tmp/{id}.sh
cat /tmp/{id}.stdout 2>/dev/null
echo "{delimeter}"
cat /tmp/{id}.stderr | sed "s/^[/\\.].*{id}.sh: //g" 2>/dev/null
echo "{delimeter}"
cat /tmp/{id}.output 2>/dev/null
'''.format(id=id, scripts=createScripts, delimeter=delimeter) if install or configure else ''

            updateScripts = '''# Scripts
exec 1>/tmp/{id}.stdout
exec 2>/tmp/{id}.stderr
output=/tmp/{id}.output
{configure}
'''.format(id=id, configure=configure)
            updateScripts = base64.b64encode(updateScripts.encode('utf-8')).decode('utf-8')
            runUpdateScripts = '''# Scripts
rm -rf /tmp/{id}.* 2>&1>/dev/null
echo "{scripts}" | base64 -d | tee /tmp/{id}.sh >/dev/null
chmod 755 /tmp/{id}.sh 2>&1>/dev/null
/tmp/{id}.sh
cat /tmp/{id}.stdout 2>/dev/null
echo "{delimeter}"
cat /tmp/{id}.stderr | sed "s/^[/\\.].*{id}.sh: //g" 2>/dev/null
echo "{delimeter}"
cat /tmp/{id}.output 2>/dev/null
'''.format(id=id, scripts=updateScripts, delimeter=delimeter) if configure else ''

        elif osType == 'windows':
            runCreateScripts = install + '\n' + configure if install or configure else ''
            runUpdateScripts = configure if configure else ''
        
        # update resource
        executions = {}
        executionIds = []
        for instance in instances:
            if instance in targets:
                if runUpdateScripts: runScripts = runUpdateScripts
                else: continue
            else:
                if runCreateScripts: runScripts = runCreateScripts
                else: continue
            res = vra.post('/vco/api/actions/fc35fa64-13ec-4fa1-8273-5d1d963521ef/executions', {
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
            })
            executions[res['execution-id']] = instance
            executionIds.append(res['execution-id'])
        executionCount = len(executionIds)
        
        completedIds = []
        executionOuts = {}
        for _ in range(0, 300):
            for executionId in executionIds:
                if executionId not in completedIds:
                    res = vra.get('/vco/api/actions/runs/' + executionId)
                    state = res['state']
                    if state == 'completed':
                        completedIds.append(executionId)
                        value = res['value'][res['type']]['value'].split(delimeter)
                        log = value[0]
                        err = value[1]
                        out = value[2].strip()
                        executionOuts[executionId] = out
                        print('<update instance="{}" resource="scripts">\n<log>{}</log>\n<err>{}</err>\n<out>{}</out>\n</update>'.format(executions[executionId], log, err, out))
                    elif state == 'failed': raise Exception(res['error'])
            if executionCount == len(completedIds): break
            time.sleep(2)
        else: raise Exception('scripts timeout')
        
        if executionCount == 1: consoleOutputs = executionOuts[executionIds[0]]
        elif executionCount > 1: consoleOutputs = [executionOuts[executionId] for executionId in executionIds]
        else: consoleOutputs = inputs['outputs']
    else: consoleOutputs = ''
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['outputs'] = consoleOutputs
    outputs['targets'] = instances
    return outputs
# __ABX_IMPLEMENTATIONS_END__
