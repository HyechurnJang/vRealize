# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

name = 'SSH' # custom resource name

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
    'address': {
        'type': 'string',
        'title': 'Address',
        'description': 'address to connect host',
    },
    'port': {
        'type': 'number',
        'title': 'Port',
        'default': 22,
        'description': 'port to connect host',
    },
    'username': {
        'type': 'string',
        'title': 'Username',
        'description': 'username in host to run scripts',
    },
    'password': {
        'type': 'string',
        'title': 'Password',
        'encrypted': True,
        'description': 'password in host to run scripts'
    },
    'create': {
        'type': 'string',
        'title': 'Create Commands',
        'default': '',
        'description': 'run script when resource created',
    },
    'update': {
        'type': 'string',
        'title': 'Update Commands',
        'default': '',
        'description': 'run script when resource updated',
    },
    'destroy': {
        'type': 'string',
        'title': 'Destroy Scripts',
        'default': '',
        'description': 'run script when resource destroyed',
    },
    'output': {
        'type': 'string',
        'title': 'Output',
        'readOnly': True,
        'default': ''
    },
}