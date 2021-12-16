# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

name = 'Project' # custom resource name

sdk = 'vra' # imported SDK at common directory

inputs = {
    'create': {
        'VraManager': 'constant'
    },
    'read': {
    },
    'update': {
        'VraManager': 'constant'
    },
    'delete': {
        'VraManager': 'constant'
    }
}

properties = {
    'name': {
        'type': 'string',
        'title': 'name',
        'description': 'Unique name of project'
    },
    'description': {
        'type': 'string',
        'title': 'description',
        'default': '',
        'description': 'Project descriptions'
    },
    'sharedResources': {
        'type': 'boolean',
        'title': 'sharedResources',
        'default': True,
        'description': 'Deployments are shared between all users in the project'
    },
    'administrators': {
        'type': 'array',
        'title': 'administrators',
        'default': [],
        'items': {
            'type': 'string'
        },
        'description': 'Accounts of administrator user'
    },
    'members': {
        'type': 'array',
        'title': 'members',
        'default': [],
        'items': {
            'type': 'string'
        },
        'description': 'Accounts of member user'
    },
    'viewers': {
        'type': 'array',
        'title': 'viewers',
        'default': [],
        'items': {
            'type': 'string'
        },
        'description': 'Accounts of viewer user'
    },
    'zones': {
        'type': 'array',
        'title': 'viewers',
        'default': [],
        'items': {
            'type': 'string'
        },
        'description': 'Specify the zones ID that can be used when users provision deployments in this project'
    },
    'placementPolicy': {
        'type': 'string',
        'title': 'placementPolicy',
        'default': 'default',
        'enum': [
            'default',
            'spread'
        ],
        'description': 'Specify the placement policy that will be applied when selecting a cloud zone for provisioning'
    },
    'customProperties': {
        'type': 'object',
        'title': 'customProperties',
        'default': {},
        'description': 'Specify the custom properties that should be added to all requests in this project'
    },
    'machineNamingTemplate': {
        'type': 'string',
        'title': 'machineNamingTemplate',
        'default': '',
        'description': 'Specify the naming template to be used for machines, networks, security groups and disks provisioned in this project'
    },
    'operationTimeout': {
        'type': 'integer',
        'title': 'operationTimeout',
        'default': 0,
        'description': 'Request timeout seconds'
    }
}