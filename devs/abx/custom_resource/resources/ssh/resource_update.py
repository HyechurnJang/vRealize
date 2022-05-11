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
    if 'address' not in inputs or not inputs['address']: raise Exception('address property must be required') # Required 
    address = inputs['address']
    port = inputs['port'] if 'port' in inputs and inputs['port'] else 22
    if 'username' not in inputs or not inputs['username']: raise Exception('username property must be required') # Required
    username = inputs['username']
    if 'password' not in inputs or not inputs['password']: raise Exception('password property must be required') # Required
    password = inputs['password'] = context.getSecret(inputs['password'])
    sync = inputs['sync'] if 'sync' in inputs and inputs['sync'] in [True, False] else True
    update = inputs['update'] if 'update' in inputs and inputs['update'] else ''
    inputs['output'] = ''
    delimeter = '__VRA_EXEC_DELIMETER__'
    
    print('[INFO] Update Description')
    print('properties.address\n{}\n'.format(address))
    print('properties.port\n{}\n'.format(port))
    print('properties.username\n{}\n'.format(username))
    print('properties.password\n{}\n'.format(password))
    print('properties.update\n{}\n'.format(update))
    
    if update:
        commands = '''# Commands
exec 1>/tmp/{id}.stdout
exec 2>/tmp/{id}.stderr
output=/tmp/{id}.output
{update}
'''.format(id=id, update=update)
        commands = base64.b64encode(commands.encode('utf-8')).decode('utf-8')
        runCommands = '''# Run Commands
rm -rf /tmp/{id}.* 2>&1>/dev/null
echo "{commands}" | base64 -d | tee /tmp/{id}.sh >/dev/null
chmod 755 /tmp/{id}.sh 2>&1>/dev/null
/tmp/{id}.sh
cat /tmp/{id}.stdout 2>/dev/null
echo "{delimeter}"
cat /tmp/{id}.stderr | sed "s/^[/\\.].*{id}.sh: //g" 2>/dev/null
echo "{delimeter}"
cat /tmp/{id}.output 2>/dev/null
'''.format(id=id, commands=commands, delimeter=delimeter)

        res = vra.post('/vco/api/actions/8cc62689-ed72-4ad7-afc6-115905681326/executions', {
            'async-execution': True,
            'parameters': [{
                'name': 'address',
                'type': 'string',
                'value': {'string': {'value': address}}
            },{
                'name': 'port',
                'type': 'number',
                'value': {'number': {'value': port}}
            },{
                'name': 'username',
                'type': 'string',
                'value': {'string': {'value': username}}
            },{
                'name': 'password',
                'type': 'string',
                'value': {'string': {'value': password}}
            },{
                'name': 'commands',
                'type': 'string',
                'value': {'string': {'value': runCommands}}
            }]
        })
        
        if sync:
            executionId = res['execution-id']
            for _ in range(0, 300):
                res = vra.get('/vco/api/actions/runs/' + executionId)
                state = res['state']
                if state == 'completed':
                    value = res['value'][res['type']]['value'].split(delimeter)
                    log = value[0]
                    error = value[1]
                    output = value[2].strip()
                    print('<update resource="ssh" address="{}" port="{}">\n<log>{}</log>\n<error>{}</error>\n<output>{}</output>\n</update>'.format(address, port, log, error, output))
                    inputs['output'] = output
                    break
                elif state == 'failed': raise Exception(res['error'])
                time.sleep(2)
            else: raise Exception('commands timeout')
        else:
            inputs['executionId'] = res['execution-id']
            inputs['output'] = ''
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    return outputs
# __ABX_IMPLEMENTATIONS_END__
