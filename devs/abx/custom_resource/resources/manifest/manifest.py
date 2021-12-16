# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

name = 'Manifest' # custom resource name

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
        'description': 'Pipeline name',
    },
    'kubernetes': {
        'type': 'string',
        'title': 'Kubernetes',
        'recreateOnUpdate': True,
        'description': 'Kubernetes cluster',
    },
    'manifest': {
        'type': 'string',
        'title': 'Manifest',
        'description': 'Manifest text',
    },
    'pipeConfig': {
        'type': 'object',
        'title': 'Pipeline Config',
        'default': {},
        'properties': {
            'orders': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'order': {
                            'type': 'array',
                            'items': {
                                'type': 'string'
                            }
                        }
                    }
                },
                'default': []
            },
            'properties': {
                'type': 'object',
                'title': 'Properties',
                'default': {}
            }
        },
        'description': 'Manifest pipeline config'
    },
    'persistence': {
        'type': 'boolean',
        'title': 'Pipeline Persistence',
        'default': False,
        'recreateOnUpdate': True,
        'description': 'Pipeline persistence option when resource deleted'
    },
}