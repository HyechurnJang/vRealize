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
import uuid
import time

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # set default values
    if 'name' not in inputs or not inputs['name']: raise Exception('name property must be required') # Required
    if 'kubernetes' not in inputs or not inputs['kubernetes']: raise Exception('kubernetes property must be required') # Required
    if 'manifest' not in inputs or not inputs['manifest']: raise Exception('manifest property must be required') # Required
    if 'pipeConfig' not in inputs: inputs['pipeConfig'] = {
        'orders': [],
        'properties': {}
    } # Optional Dict Init
    if 'persistence' not in inputs: inputs['persistence'] = False # Optional Init
    
    name = inputs['name']
    kubernetes = inputs['kubernetes']
    manifest = inputs['manifest']
    pipeConfig = inputs['pipeConfig']
    if 'orders' not in pipeConfig: pipeConfig['orders'] = []
    if 'properties' not in pipeConfig: pipeConfig['properties'] = {}
    for metaName, property in pipeConfig['properties'].items():
        if 'ignoreFailure' not in property: property['ignoreFailure'] = True
        if isinstance(property['ignoreFailure'], str):
            ignoreFailure = property['ignoreFailure'].lower()
            if ignoreFailure not in ['true', 'false']: raise Exception('property[{}].ignoreFailure must be true or false'.format(metaName))
            else:
                if ignoreFailure == 'true': property['ignoreFailure'] = True
                else: property['ignoreFailure'] = False
        if 'timeout' not in property: property['timeout'] = 10
        if not isinstance(property['timeout'], int): raise Exception('property[{}].timeout must be number'.format(metaName))
    persistence = inputs['persistence']
    
    metaNames = []
    metaOrders = []
    for order in pipeConfig['orders']:
        if 'order' in order:
            for metaName in order['order']:
                if metaName in metaNames: raise Exception('meta[{}] must be at one order'.format(metaName))
            metaOrders.append(order['order'])
    
    taskOrders = [ [] for _ in metaOrders ]
    notOrderedTaskOrders = []
    taskApply = {}
    taskDelete = {}
    joinedTaskOrders = []
    for yml in manifest.strip().split('---'):
        if yml:
            innerMetadata = False
            for line in yml.strip().split(_NEWLINE_):
                if innerMetadata:
                    if 'name:' in line:
                        metaName = line.split('name:')[1].strip()
                        break
                else:
                    if 'metadata:' in line and line.index('metadata:') == 0: innerMetadata = True
            else: raise Exception('could not find metadata.name in manifest')
            taskName = str(uuid.uuid4())
            for index in range(0, len(metaOrders)):
                if metaName in metaOrders[index]:
                    taskOrders[index].append(taskName)
                    break
            else: notOrderedTaskOrders.append(taskName)
            try: ignoreFailure = pipeConfig['properties'][metaName]['ignoreFailure']
            except: ignoreFailure = False
            try: timeout = pipeConfig['properties'][metaName]['timeout']
            except: timeout = 10
            taskApply[taskName] = {
                'type': 'K8S',
                'ignoreFailure': ignoreFailure,
                'preCondition': '${input.method}=="apply"',
                'input': {
                    'action': 'APPLY',
                    'timeout': timeout,
                    'filePath': '',
                    'scmConstants': {},
                    'yaml': yml
                },
                'endpoints': {'kubernetesServer': kubernetes},
                'tags': [],
                '_configured': True
            }
            taskDelete[taskName] = {
                'type': 'K8S',
                'ignoreFailure': True,
                'preCondition': '${input.method}=="delete"',
                'input': {
                    'action': 'DELETE',
                    'timeout': timeout,
                    'filePath': '',
                    'scmConstants': {},
                    'yaml': yml
                },
                'endpoints': {'kubernetesServer': kubernetes},
                'tags': [],
                '_configured': True
            }
    
    for order in taskOrders:
        if order:
            if len(order) > 24: raise Exception('order items could not be over 24 items')
            joinedTaskOrders.append(','.join(order))
    
    taskOrders = joinedTaskOrders
    if len(notOrderedTaskOrders) > 24: raise Exception('non-ordered items are over 24 items')
    taskOrders.append(','.join(notOrderedTaskOrders))
    taskOrdersApply = taskOrders
    taskOrdersDelete = list(taskOrders)
    taskOrdersDelete.reverse()
    
    # create resource
    endpoint = vra.get("/codestream/api/endpoints?$filter=(name eq '{}')".format(kubernetes))
    try: endpoint = endpoint['documents'][endpoint['links'][0]]
    except: raise Exception('could not find kubernetes : ' + kubernetes)
    
    resource = vra.post('/codestream/api/pipelines', {
        'project': endpoint['project'],
        'kind': 'PIPELINE',
        'name': '{}-{}'.format(name, str(uuid.uuid4())),
        'description': 'vra-custom-resource',
        'enabled': True,
        'concurrency': 1,
        'input': {'method': ''},
        'output': {},
        'starred': {},
        'stageOrder': ['Apply', 'Delete'],
        'stages': {
            'Apply': {
                'taskOrder': taskOrdersApply,
                'tasks': taskApply,
                'tags': []    
            },
            'Delete': {
                'taskOrder': taskOrdersDelete,
                'tasks': taskDelete,
                'tags': []
            }
        },
        'notifications': {'email': [], 'jira': [], 'webhook': []},
        'options': [],
        'workspace': {
            'image': '',
            'path': '',
            'type': 'DOCKER',
            'endpoint': '',
            'customProperties': {},
            'cache': [],
            'registry': '',
            'limits': {'cpu': 1.0, 'memory': 512},
            'autoCloneForTrigger': False,
            'environmentVariables': {}
        },
        '_inputMeta': {'method': {'description': '', 'mandatory': True}},
        '_outputMeta': {},
        '_warnings': [],
        'rollbacks': [],
        'tags': []
    })
    
    ## change state to enabled
    vra.patch('/codestream/api/pipelines/' + resource['id'], {'state': 'ENABLED'});
    
    ## execute apply method on pipeline
    try: executionLink = vra.post('/codestream/api/pipelines/{}/executions'.format(resource['id']), {'input': {'method': 'apply'}})['executionLink']
    except: 
        if not persistence:
            try: vra.delete('/codestream/api/pipelines/' + resource['id'])
            except: pass
        raise Exception('could not execute pipeline')
    
    for _ in range(0, 300):
        execution = vra.get(executionLink)
        if execution['status'] == 'COMPLETED': break
        elif execution['status'] == 'FAILED':
            vra.post('/codestream/api/pipelines/{}/executions'.format(resource['id']), {'input': {'method': 'delete'}})
            if not persistence:
                try: vra.delete('/codestream/api/pipelines/' + resource['id'])
                except: pass
            raise Exception('pipeline execution failed : ' + execution['statusMessage'])
        time.sleep(3)
    else:
        vra.post('/codestream/api/pipelines/{}/executions'.format(resource['id']), {'input': {'method': 'delete'}})
        if not persistence:
            try: vra.delete('/codestream/api/pipelines/' + resource['id'])
            except: pass
        raise Exception('pipeline execution might be stuck over 15 min')
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['id'] = resource['id']
    return outputs
# __ABX_IMPLEMENTATIONS_END__
