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
import re
import uuid
import time

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # set default values
    if 'name' not in inputs or not inputs['name']: raise Exception('name property must be required') # Required
    name = inputs['name']
    if 'clusterType' not in inputs or not inputs['clusterType'] or inputs['clusterType'] not in ['tanzu', 'external']: raise Exception('clusterType property must be required') # Required
    if inputs['clusterType'] == 'tanzu':
        if 'cluster' not in inputs or not inputs['cluster']: raise Exception('cluster property must be required') # Required
        cluster = inputs['cluster']
        headers = {
            'Authorization': vra.headers['Authorization'],
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8,ko-KR;q=0.7'
        }
        kubeConfig = requests.get('https://{}{}/kube-config'.format(vra.hostname, cluster), headers=headers)
        kubeConfig.raise_for_status()
        kubeConfig = kubeConfig.text
        projectId = vra.get(cluster)['projectId']
        projectName = vra.get('/iaas/api/projects/{}'.format(projectId))['name']
    elif inputs['clusterType'] == 'external':
        if 'kubeConfig' not in inputs or not inputs['kubeConfig']: raise Exception('kubeConfig property must be required') # Required
        if 'project' not in inputs or not inputs['project']: raise Exception('project property must be required') # Required
        kubeConfig = inputs['kubeConfig']
        projectName = inputs['project']
        try: projectId = vra.get("/iaas/api/projects?$filter=(name eq 'ADMIN')")['content'][0]['id']
        except Exception as e: raise Exception('could not find project')
    
    try : server = re.search('server: ["\']?(?P<value>https?://\w[\w\.]+(:\d+)?)["\']?', kubeConfig)['value']
    except Exception as e: raise Exception('could not find server')
    try: ca = re.search('certificate-authority-data: ["\']?(?P<value>\w+\=*)["\']?', kubeConfig)['value']
    except Exception as e: raise Exception('could not find certificate-authority-data')
    try:
        cert = re.search('client-certificate-data: ["\']?(?P<value>\w+\=*)["\']?', kubeConfig)['value']
        key = re.search('client-key-data: ["\']?(?P<value>\w+\=*)["\']?', kubeConfig)['value']
    except Exception as e: raise Exception('could not find cert and key')
    if inputs['clusterManifest'] not in inputs or not inputs['clusterManifest']: inputs['clusterManifest'] = ''
    clusterManifest = inputs['clusterManifest']
    
    # create resource
    if inputs['clusterType'] == 'external':
        cluster = '/cmx/api/resources/k8s/clusters/' + vra.post('/cmx/api/resources/k8s/clusters', {
            'project': projectId,
            'name': name,
            'address': server,
            'clusterType': 'EXTERNAL',
            'caCertificate': ca,
            'credentials': {
                'type': 'PublicKey',
                'publicKey': cert,
                'privateKey': key
            }
        })['id']
    
    req = {
        'project': projectName,
        'name': name,
        'type': 'k8s',
        'isRestricted': False,
        'properties': {
            'kubernetesURL': server,
            'authType': 'certificate',
            'certAuthorityData': ca,
            'certData': cert,
            'certKeyData': key,
            'fingerprint': vra.get('/codestream/api/endpoint-certificate?url={}'.format(server))['certificates'][0]['fingerprints']['SHA-256']
        }
    }
    vra.post('/codestream/api/endpoint-validation', req)
    resource = vra.post('/codestream/api/endpoints', req)
    
    if clusterManifest:
        pipeline = vra.post('/codestream/api/pipelines', {
            'project': projectId,
            'kind': 'PIPELINE',
            'name': '{}-{}'.format(name, str(uuid.uuid4())),
            'description': 'kubernetes-initial-manifest',
            'enabled': True,
            'concurrency': 1,
            'input': {'method': ''},
            'output': {},
            'starred': {},
            'stageOrder': ['Config'],
            'stages': {
                'Config': {
                    'taskOrder': [['Initial']],
                    'tasks': {
                        'Initial': {
                            'type': 'K8S',
                            'ignoreFailure': True,
                            'preCondition': '',
                            'input': {
                                'action': 'APPLY',
                                'timeout': 15,
                                'filePath': '',
                                'scmConstants': {},
                                'yaml': clusterManifest
                            },
                            'endpoints': {'kubernetesServer': name},
                            'tags': [],
                            '_configured': True
                        }
                    },
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
        
        vra.patch('/codestream/api/pipelines/' + pipeline['id'], {'state': 'ENABLED'})
        vra.post('/codestream/api/pipelines/{}/executions'.format(pipeline['id']), {})
        time.sleep(1)
        vra.delete('/codestream/api/pipelines/' + pipeline['id'])
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['id'] = resource['id']
    outputs['cluster'] = cluster
    outputs['project'] = projectName
    outputs['kubeConfig'] = kubeConfig
    
    return outputs
# __ABX_IMPLEMENTATIONS_END__
