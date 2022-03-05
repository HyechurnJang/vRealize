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
import uuid
import time
import base64
import subprocess

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # set default values
    id = str(uuid.uuid4())
    instances = inputs['instances'] if 'instances' in inputs and inputs['instances'] else [] 
    if 'username' not in inputs or not inputs['username']: raise Exception('username property must be required') # Required
    username = inputs['username']
    if 'password' not in inputs or not inputs['password']: raise Exception('password property must be required') # Required
    password = inputs['password'] = context.getSecret(inputs['password'])
    keySize = inputs['keySize'] if 'keySize' in inputs and inputs['keySize'] else 2048
    privateKey = subprocess.run('openssl genrsa {}'.format(keySize), shell=True, check=True, capture_output=True).stdout.decode('utf-8').strip()
    
    print('[INFO] Create Cert Description')
    print('properties.instances\n{}\n'.format(instances))
    print('properties.username\n{}\n'.format(username))
    print('properties.password\n{}\n'.format(password))
    print('properties.keySize\n{}\n'.format(keySize))
    print('properties.privateKey\n{}\n'.format(privateKey))
    
    b64Key = base64.b64encode(privateKey.encode('utf-8')).decode('utf-8')
    scripts = '''# Scripts
mkdir -p ~/.ssh
echo "{}" | base64 -d | tee ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa
ssh-keygen -f ~/.ssh/id_rsa -y >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
'''.format(b64Key)

    print(scripts)
    
        # create resource
    executions = {}
    executionIds = []
    for instance in instances:
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
                'value': {'string': {'value': scripts}}
            }]
        })
        executions[res['execution-id']] = instance
        executionIds.append(res['execution-id'])
    executionCount = len(executionIds)
    
    completedIds = []
    for _ in range(0, 150):
        for executionId in executionIds:
            if executionId not in completedIds:
                res = vra.get('/vco/api/actions/runs/' + executionId)
                state = res['state']
                if state == 'completed':
                    completedIds.append(executionId)
                    print('<create instance="{}" resource="cert">{}</create>'.format(executions[executionId], privateKey))
                elif state == 'failed': raise Exception(res['error'])
        if executionCount == len(completedIds): break
        time.sleep(2)
    else: raise Exception('scripts timeout')
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['id'] = id
    outputs['privateKey'] = privateKey
    outputs['targets'] = instances
    return outputs
# __ABX_IMPLEMENTATIONS_END__
