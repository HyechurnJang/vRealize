# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

name = 'HCDeployment' # custom resource name

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
        'title': 'Name',
        'recreateOnUpdate': True,
        'description': 'Unique name of deployment'
    },
    'projectName': {
        'type': 'string',
        'title': 'Project',
        'recreateOnUpdate': True,
        'description': 'Assigned project'        
    },
    'itemType': {
        'type': 'string',
        'title': 'Contents Type',
        'enum': [
            'blueprint',
            'catalog'
        ],
        'recreateOnUpdate': True,
        'description': 'Contents from blueprint or catalog'
    },
    'itemName': {
        'type': 'string',
        'title': 'Contents',
        'recreateOnUpdate': True,
        'description': 'Contents name to deploy'
    },
    'inputs': {
        'type': 'object',
        'title': 'Inputs',
        'default': {},
        'description': 'Inputs parameters to deploy'
    }
}