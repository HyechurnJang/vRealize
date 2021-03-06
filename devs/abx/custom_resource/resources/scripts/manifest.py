# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

name = 'Scripts' # custom resource name

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
    'instances': {
        'type': 'array',
        'title': 'Instances',
        'items': {
            'type': 'string'
        },
        'description': 'instance array to run scripts'
    },
    'osType': {
        'type': 'string',
        'title': 'OS Type',
        'enum': ['linux', 'windows'],
        'description': 'os type to run scripts'
    },
    'username': {
        'type': 'string',
        'title': 'Username',
        'description': 'username in vm to run scripts',
    },
    'password': {
        'type': 'string',
        'title': 'Password',
        'encrypted': True,
        'description': 'password in vm to run scripts'
    },
    'install': {
        'type': 'string',
        'title': 'Install Scripts',
        'default': '',
        'description': 'only run script when first deployed',
    },
    'configure': {
        'type': 'string',
        'title': 'Configure Scripts',
        'default': '',
        'description': 'run script when post install and scripts updated',
    },
    'destroy': {
        'type': 'string',
        'title': 'Destroy Scripts',
        'default': '',
        'description': 'run script when destroyed',
    },
    'targets': {
        'type': 'array',
        'title': 'Targets',
        'readOnly': True,
        'items': {
            'type': 'string'
        },
        'default': []
    },
    'outputs': {
        'type': 'string',
        'title': 'Outputs',
        'readOnly': True,
        'default': ''
    },
}