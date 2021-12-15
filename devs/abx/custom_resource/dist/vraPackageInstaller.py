# -*- coding: utf-8 -*-
'''
Created on 2021. 11. 18.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

constDescs = {}

rscDescs = {
'HCProject': {
    'inputs': {'create': {'VraManager': 'constant'}, 'read': {}, 'update': {'VraManager': 'constant'}, 'delete': {'VraManager': 'constant'}},
    'properties': {'name': {'type': 'string', 'title': 'name', 'description': 'Unique name of project'}, 'description': {'type': 'string', 'title': 'description', 'default': '', 'description': 'Project descriptions'}, 'sharedResources': {'type': 'boolean', 'title': 'sharedResources', 'default': True, 'description': 'Deployments are shared between all users in the project'}, 'administrators': {'type': 'array', 'title': 'administrators', 'default': [], 'items': {'type': 'string'}, 'description': 'Accounts of administrator user'}, 'members': {'type': 'array', 'title': 'members', 'default': [], 'items': {'type': 'string'}, 'description': 'Accounts of member user'}, 'viewers': {'type': 'array', 'title': 'viewers', 'default': [], 'items': {'type': 'string'}, 'description': 'Accounts of viewer user'}, 'zones': {'type': 'array', 'title': 'viewers', 'default': [], 'items': {'type': 'string'}, 'description': 'Specify the zones ID that can be used when users provision deployments in this project'}, 'placementPolicy': {'type': 'string', 'title': 'placementPolicy', 'default': 'DEFAULT', 'enum': ['DEFAULT', 'SPREAD'], 'description': 'Specify the placement policy that will be applied when selecting a cloud zone for provisioning'}, 'customProperties': {'type': 'object', 'title': 'customProperties', 'default': {}, 'description': 'Specify the custom properties that should be added to all requests in this project'}, 'machineNamingTemplate': {'type': 'string', 'title': 'machineNamingTemplate', 'default': '', 'description': 'Specify the naming template to be used for machines, networks, security groups and disks provisioned in this project'}, 'operationTimeout': {'type': 'integer', 'title': 'operationTimeout', 'default': 0, 'description': 'Request timeout seconds'}},
    'sdk': '''#===============================================================================
# Rest SDK Implementation                                                      #
#===============================================================================
import ssl
import json as JSON
import typing
import urllib.error
import urllib.request
from email.message import Message

class Response(typing.NamedTuple):
    text: str
    headers: Message
    status: int
    def json(self) -> typing.Any:
        try: output = JSON.loads(self.text)
        except JSON.JSONDecodeError: output = ''
        return output
    def raise_for_status(self):
        if self.status >= 400: raise Exception('response error with status code {}'.format(self.status))
        return self

class requests:
    @classmethod
    def __headers__(cls, headers):
        headers = headers or {}
        if 'Accept' not in headers: headers['Accept'] = 'application/json'
        if 'Content-Type' not in headers: headers['Content-Type'] = 'application/json'
        return headers
    @classmethod
    def __payload__(cls, data, json):
        if data: return data.encode('utf-8')
        elif json: return JSON.dumps(json).encode('utf-8')
        else: return ''.encode('utf-8')
    @classmethod
    def __encode__(cls, url): return url.replace(' ', '%20').replace('$', '%24').replace("'", '%27').replace('[', '%5B').replace(']', '%5D')
    @classmethod
    def __call__(cls, httprequest):
        try:
            with urllib.request.urlopen(httprequest, context=ssl._create_unverified_context()) as httpresponse: response = Response(text=httpresponse.read().decode(httpresponse.headers.get_content_charset('utf-8')), headers=httpresponse.headers, status=httpresponse.status)
        except urllib.error.HTTPError as e: response = Response(text=e.fp.read().decode('utf-8'), headers=e.headers, status=e.code)
        return response
    @classmethod
    def get(cls, url:str, headers:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='GET', headers=cls.__headers__(headers)))
    @classmethod
    def post(cls, url:str, headers:dict=None, data:str=None, json:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='POST', headers=cls.__headers__(headers), data=cls.__payload__(data, json)))
    @classmethod
    def put(cls, url:str, headers:dict=None, data:str=None, json:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='PUT', headers=cls.__headers__(headers), data=cls.__payload__(data, json)))
    @classmethod
    def patch(cls, url:str, headers:dict=None, data:str=None, json:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='PATCH', headers=cls.__headers__(headers), data=cls.__payload__(data, json)))
    @classmethod
    def delete(cls, url:str, headers:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='DELETE', headers=cls.__headers__(headers)))

class VraManager:
    def __init__(self, context, inputs):
        self.hostname = context.getSecret(inputs['VraManager']['hostname'])
        self.headers = {}
        data = self.post('/csp/gateway/am/api/login?access_token', {'username': context.getSecret(inputs['VraManager']['username']), 'password': context.getSecret(inputs['VraManager']['password'])})
        data = self.post('/iaas/api/login', {'refreshToken': data['refresh_token']})
        self.headers['Authorization'] = 'Bearer ' + data['token']
    def toJson(self, response):
        try: response.raise_for_status()
        except Exception as e:
            try: data = JSON.dumps(response.json(), indent=2)
            except: data = response.text
            raise Exception('{} : {}'.format(str(e), data))
        return response.json()
    def get(self, url:str) -> dict: return self.toJson(requests.get('https://{}{}'.format(self.hostname, url), headers=self.headers))
    def post(self, url:str, data:dict=None) -> dict: return self.toJson(requests.post('https://{}{}'.format(self.hostname, url), headers=self.headers, json=data))
    def put(self, url:str, data:dict=None) -> dict: return self.toJson(requests.put('https://{}{}'.format(self.hostname, url), headers=self.headers, json=data))
    def patch(self, url:str, data:dict=None) -> dict: return self.toJson(requests.patch('https://{}{}'.format(self.hostname, url), headers=self.headers, json=data))
    def delete(self, url:str) -> dict: return self.toJson(requests.delete('https://{}{}'.format(self.hostname, url), headers=self.headers))''',
    'createHandler': '''#===============================================================================
# ABX Code Implementations                                                     #
#===============================================================================
# Import Libraries Here

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # set default values
    if 'description' not in inputs: inputs['description'] = ''
    if 'sharedResources' not in inputs: inputs['sharedResources'] = True
    if 'administrators' not in inputs: inputs['administrators'] = []
    if 'members' not in inputs: inputs['members'] = []
    if 'viewers' not in inputs: inputs['viewers'] = []
    if 'zones' not in inputs: inputs['zones'] = []
    if 'placementPolicy' not in inputs: inputs['placementPolicy'] = 'DEFAULT'
    if 'customProperties' not in inputs: inputs['customProperties'] = {}
    if 'machineNamingTemplate' not in inputs: inputs['machineNamingTemplate'] = ''
    if 'operationTimeout' not in inputs: inputs['operationTimeout'] = 0
    
    # create resource
    resource = vra.post('/iaas/api/projects', {
        'name': inputs['name'],
        'description': inputs['description'],
        'sharedResources': inputs['sharedResources'],
        'administrators': [{'type': 'user', 'email': account} for account in inputs['administrators']],
        'members': [{'type': 'user', 'email': account} for account in inputs['members']],
        'viewers': [{'type': 'user', 'email': account} for account in inputs['viewers']],
        'zones': [{'zoneId': zoneId} for zoneId in inputs['zones']],
        'placementPolicy': inputs['placementPolicy'],
        'customProperties': inputs['customProperties'],
        'machineNamingTemplate': inputs['machineNamingTemplate'],
        'operationTimeout': inputs['operationTimeout']
    })
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['id'] = resource['id']
    return outputs''',
    'readHandler': '''#===============================================================================
# ABX Code Implementations                                                     #
#===============================================================================
# Import Libraries Here

# Implement Handler Here
def handler(context, inputs):
    # bypass resource
    return inputs''',
    'deleteHandler': '''#===============================================================================
# ABX Code Implementations                                                     #
#===============================================================================
# Import Libraries Here

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # delete resource
    vra.delete('/iaas/api/projects/' + inputs['id'])
    
    # publish resource
    return {}''',
    'updateHandler': '''#===============================================================================
# ABX Code Implementations                                                     #
#===============================================================================
# Import Libraries Here

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # retrieve resource
    resource = vra.get('/iaas/api/projects/' + inputs['id'])
    
    # update resource
    if 'name' in inputs: resource['name'] = inputs['name']
    if 'description' in inputs: resource['description'] = inputs['description']
    if 'sharedResources' in inputs: resource['sharedResources'] = inputs['sharedResources']
    if 'administrators' in inputs and inputs['administrators']: resource['administrators'] = [{'type': 'user', 'email': account} for account in inputs['administrators']]
    if 'members' in inputs and inputs['members']: resource['members'] = [{'type': 'user', 'email': account} for account in inputs['members']]
    if 'viewers' in inputs and inputs['viewers']: resource['viewers'] = [{'type': 'user', 'email': account} for account in inputs['viewers']]
    if 'zones' in inputs and inputs['zones']: resource['zoneAssignmentConfigurations'] = [{'zoneId': zoneId} for zoneId in inputs['zones']]
    if 'placementPolicy' in inputs: resource['placementPolicy'] = inputs['placementPolicy']
    if 'customProperties' in inputs: resource['customProperties'] = inputs['customProperties']
    if 'machineNamingTemplate' in inputs: resource['machineNamingTemplate'] = inputs['machineNamingTemplate']
    if 'operationTimeout' in inputs: resource['operationTimeout'] = inputs['operationTimeout']
    vra.patch('/iaas/api/projects/' + inputs['id'], resource)
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    return outputs''',
},
}

#===============================================================================
# Rest SDK Implementation                                                      #
#===============================================================================
import ssl
import json as JSON
import typing
import urllib.error
import urllib.request
from email.message import Message

class Response(typing.NamedTuple):
    text: str
    headers: Message
    status: int
    def json(self) -> typing.Any:
        try: output = JSON.loads(self.text)
        except JSON.JSONDecodeError: output = ''
        return output
    def raise_for_status(self):
        if self.status >= 400: raise Exception('response error with status code {}'.format(self.status))
        return self

class requests:
    @classmethod
    def __headers__(cls, headers):
        headers = headers or {}
        if 'Accept' not in headers: headers['Accept'] = 'application/json'
        if 'Content-Type' not in headers: headers['Content-Type'] = 'application/json'
        return headers
    @classmethod
    def __payload__(cls, data, json):
        if data: return data.encode('utf-8')
        elif json: return JSON.dumps(json).encode('utf-8')
        else: return ''.encode('utf-8')
    @classmethod
    def __encode__(cls, url): return url.replace(' ', '%20').replace('$', '%24').replace("'", '%27').replace('[', '%5B').replace(']', '%5D')
    @classmethod
    def __call__(cls, httprequest):
        try:
            with urllib.request.urlopen(httprequest, context=ssl._create_unverified_context()) as httpresponse: response = Response(text=httpresponse.read().decode(httpresponse.headers.get_content_charset('utf-8')), headers=httpresponse.headers, status=httpresponse.status)
        except urllib.error.HTTPError as e: response = Response(text=e.fp.read().decode('utf-8'), headers=e.headers, status=e.code)
        return response
    @classmethod
    def get(cls, url:str, headers:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='GET', headers=cls.__headers__(headers)))
    @classmethod
    def post(cls, url:str, headers:dict=None, data:str=None, json:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='POST', headers=cls.__headers__(headers), data=cls.__payload__(data, json)))
    @classmethod
    def put(cls, url:str, headers:dict=None, data:str=None, json:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='PUT', headers=cls.__headers__(headers), data=cls.__payload__(data, json)))
    @classmethod
    def patch(cls, url:str, headers:dict=None, data:str=None, json:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='PATCH', headers=cls.__headers__(headers), data=cls.__payload__(data, json)))
    @classmethod
    def delete(cls, url:str, headers:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='DELETE', headers=cls.__headers__(headers)))

class VraManager:
    def __init__(self, context, inputs):
        self.hostname = inputs['vraHostname']
        self.headers = {}
        data = self.post('/csp/gateway/am/api/login?access_token', {'username': inputs['vraUsername'], 'password': inputs['vraPassword']})
        data = self.post('/iaas/api/login', {'refreshToken': data['refresh_token']})
        self.headers['Authorization'] = 'Bearer ' + data['token']
    def toJson(self, response):
        try: response.raise_for_status()
        except Exception as e:
            try: data = JSON.dumps(response.json(), indent=2)
            except: data = response.text
            raise Exception('{} : {}'.format(str(e), data))
        return response.json()
    def get(self, url:str) -> dict: return self.toJson(requests.get('https://{}{}'.format(self.hostname, url), headers=self.headers))
    def post(self, url:str, data:dict=None) -> dict: return self.toJson(requests.post('https://{}{}'.format(self.hostname, url), headers=self.headers, json=data))
    def put(self, url:str, data:dict=None) -> dict: return self.toJson(requests.put('https://{}{}'.format(self.hostname, url), headers=self.headers, json=data))
    def patch(self, url:str, data:dict=None) -> dict: return self.toJson(requests.patch('https://{}{}'.format(self.hostname, url), headers=self.headers, json=data))
    def delete(self, url:str) -> dict: return self.toJson(requests.delete('https://{}{}'.format(self.hostname, url), headers=self.headers))
    
    def findProject(self, name):
        for project in self.get("/iaas/api/projects?$filter=(name eq '{}')".format(name))['content']:
            if project['name'] == name: return project
        else: raise Exception('could not find project : {}'.format(name))
        
    def createConstant(self, name, value, encrypted=False):
        for constant in self.get('/abx/api/resources/action-secrets')['content']:
            if constant['name'] == name:
                print('Update Constant : {}'.format(name))
                constant['encrypted'] = encrypted
                constant['value'] = value
                return self.put('/abx/api/resources/action-secrets/' + constant['id'], constant)
        else:
            print('Create Constant : {}'.format(name))
            return self.post('/abx/api/resources/action-secrets', {
                'name': name,
                'encrypted': encrypted,
                'value': value
            })
            
    def createAction(self, name, project, inputs, sdk, handler):
        projectId = project['id']
        actionSource = """# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

%s

%s
""" % (sdk, handler)
        for action in self.get("/abx/api/resources/actions?$filter=(name eq '{}')".format(name))['content']:
            if action['name'] == name and action['projectId'] == projectId:
                isUpdate = False
                if action['source'] != actionSource: isUpdate = True
                else:
                    for ak, av in action['inputs'].items():
                        for ik, iv in inputs.items():
                            if ak == ik and av == iv: break
                        else: isUpdate = True
                if not isUpdate:
                    print('Bypass Action : {}'.format(name))
                    return action
                else:
                    print('Update Action : {}'.format(name))
                    action['inputs'] = inputs
                    action['source'] = actionSource
                    return self.put('/abx/api/resources/actions/' + action['id'], action)
        else:
            print('Create Action : {}'.format(name))
            return self.post('/abx/api/resources/actions', {
                'name': name,
                'projectId': projectId,
                'inputs': inputs,
                'source': actionSource,
                'memoryInMB': 300,
                'timeoutSeconds': 600,
                'scalable': False,
                'shared': True,
                'actionType': 'SCRIPT',
                'entrypoint': 'handler',
                'scriptSource': 0,
                'runtime': 'python',
                'configuration': {},
                'provider': '',
                'metadata': { 'actionIsRetriable': False }
            })
            
    def createResource(self, name, properties, actionCreate, actionRead, actionUpdate, actionDelete):
        for resource in self.get("/form-service/api/custom/resource-types?$filter=(displayName eq '{}')".format(name))['content']:
            if resource['displayName'] == name:
                print('Update Resource : {}'.format(name))
                mainActions = resource['mainActions']
                mainActions['create'] = {
                    "id": actionCreate['id'],
                    "name": actionCreate['name'],
                    "projectId": actionCreate['projectId'],
                    "type": "abx.action"
                }
                mainActions['read'] = {
                    "id": actionRead['id'],
                    "name": actionRead['name'],
                    "projectId": actionRead['projectId'],
                    "type": "abx.action"
                }
                if actionUpdate:
                    mainActions['update'] = {
                        "id": actionUpdate['id'],
                        "name": actionUpdate['name'],
                        "projectId": actionUpdate['projectId'],
                        "type": "abx.action"
                    }
                elif 'update' in mainActions: mainActions.pop('update')
                mainActions['delete'] = {
                    "id": actionDelete['id'],
                    "name": actionDelete['name'],
                    "projectId": actionDelete['projectId'],
                    "type": "abx.action"
                }
                resource['properties']['properties'] = properties
                return self.post('/form-service/api/custom/resource-types', resource)
        else:
            print('Create Resource : {}'.format(name))
            resource = {
                "displayName": name,
                "description": "",
                "resourceType": "Custom.{}".format(name),
                "externalType": None,
                "status": "RELEASED",
                "schemaType": "ABX_USER_DEFINED",
                "properties": {
                    "properties": properties
                },
                "additionalActions": [
                ],
                "mainActions": {
                    "create": {
                        "id": actionCreate['id'],
                        "name": actionCreate['name'],
                        "projectId": actionCreate['projectId'],
                        "type": "abx.action"
                    },
                    "read": {
                        "id": actionRead['id'],
                        "name": actionRead['name'],
                        "projectId": actionRead['projectId'],
                        "type": "abx.action"
                    },
                    "delete": {
                        "id": actionDelete['id'],
                        "name": actionDelete['name'],
                        "projectId": actionDelete['projectId'],
                        "type": "abx.action"
                    }
                }
            }
            if actionUpdate:
                resource['mainActions']['update'] = {
                    "id": actionUpdate['id'],
                    "name": actionUpdate['name'],
                    "projectId": actionUpdate['projectId'],
                    "type": "abx.action"
                }
            return self.post('/form-service/api/custom/resource-types', resource)

#===============================================================================
# ABX Code Implementations                                                     #
#===============================================================================
# Import Libraries Here

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # get project
    project = vra.findProject(inputs['vraProject'])
    
    # create constants
    constants = {}
    constants['VraManager'] = vra.createConstant('VraManager', {
        'hostname': inputs['vraHostname'],
        'username': inputs['vraUsername'],
        'password': inputs['vraPassword']
    }, encrypted=True)
    for constName, constDesc in constDescs.items():
        constRequest = {}
        for k, v in constDesc['map'].items(): constRequest[v] = inputs[k]
        constants[constName] = vra.createConstant(constName, constRequest, encrypted=constDesc['encrypted'] if 'encrypted' in constDesc else False)
    
    # create custom resources
    for rscName, rscDesc in rscDescs.items():
        # create create action
        actionInputs = {}
        for k, v in rscDesc['inputs']['create'].items():
            if v == 'default' : actionInputs[k] = ''
            elif v == 'constant': actionInputs['secret:' + constants[k]['id']] = ''
        actionCreate = vra.createAction('Custom.{}.create()'.format(rscName), project, actionInputs, rscDesc['sdk'], rscDesc['createHandler'])
        # create read action
        actionInputs = {}
        for k, v in rscDesc['inputs']['read'].items():
            if v == 'default' : actionInputs[k] = ''
            elif v == 'constant': actionInputs['secret:' + constants[k]['id']] = ''
        actionRead = vra.createAction('Custom.{}.read()'.format(rscName), project, actionInputs, rscDesc['sdk'], rscDesc['readHandler'])
        # create update action
        if 'updateHandler' in rscDesc:
            actionInputs = {}
            for k, v in rscDesc['inputs']['update'].items():
                if v == 'default' : actionInputs[k] = ''
                elif v == 'constant': actionInputs['secret:' + constants[k]['id']] = ''
            actionUpdate = vra.createAction('Custom.{}.update()'.format(rscName), project, actionInputs, rscDesc['sdk'], rscDesc['updateHandler'])
        else: actionUpdate = None
        # create delete action
        actionInputs = {}
        for k, v in rscDesc['inputs']['delete'].items():
            if v == 'default' : actionInputs[k] = ''
            elif v == 'constant': actionInputs['secret:' + constants[k]['id']] = ''
        actionDelete = vra.createAction('Custom.{}.delete()'.format(rscName), project, actionInputs, rscDesc['sdk'], rscDesc['deleteHandler'])
        # create resource
        vra.createResource(rscName, rscDesc['properties'], actionCreate, actionRead, actionUpdate, actionDelete)
    
    return {}
