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
    if 'username' not in inputs or not inputs['username']: raise Exception('username property must be required') # Required
    if 'password' not in inputs or not inputs['password']: raise Exception('password property must be required') # Required
    if 'keySize' not in inputs or not inputs['keySize']: inputs['keySize'] = 2048
    
    id = inputs['id']
    instances = inputs['instances']
    targets = inputs['targets']
    privateKey = inputs['privateKey']
    username = inputs['username']
    password = inputs['password'] = context.getSecret(inputs['password'])
    
    b64Key = base64.b64encode(privateKey.encode('utf-8')).decode('utf-8')
    scripts = """# Register Cert
mkdir -p ~/.ssh
echo "{}" | base64 -d | tee ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa
ssh-keygen -f ~/.ssh/id_rsa -y >> ~/.ssh/authorized_keys
""".format(b64Key)
    
    # update resource
    executions = {}
    executionIds = []
    for instance in instances:
        if instance not in targets:
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
                    'value': {'string': {'value': scripts}}
                }]
            }
            res = vra.post('/vco/api/actions/fc35fa64-13ec-4fa1-8273-5d1d963521ef/executions', req);
            executions[res['execution-id']] = instance
            executionIds.append(res['execution-id'])
    executionCount = len(executionIds)
    
    completedIds = []
    for _ in range(0, 180):
        for executionId in executionIds:
            if executionId not in completedIds:
                res = vra.get('/vco/api/actions/runs/' + executionId)
                state = res['state']
                if state == 'completed':
                    completedIds.append(executionId)
                    print('<create instance="{}" resource="cert">{}</create>'.format(executions[executionId], privateKey))
                elif state == 'failed': raise Exception(res['error'])
        if executionCount == len(completedIds): break
        time.sleep(5)
    else: raise Exception('scripts timeout')
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['id'] = id
    outputs['privateKey'] = privateKey
    outputs['targets'] = instances
    return outputs
# __ABX_IMPLEMENTATIONS_END__
