# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

name = 'Cert' # custom resource name

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
        'description': 'instance array to share cert'
    },
    'username': {
        'type': 'string',
        'title': 'Username',
        'description': 'username in vm to share cert',
    },
    'password': {
        'type': 'string',
        'title': 'Password',
        'encrypted': True,
        'description': 'password in vm to share cert'
    },
    'keySize': {
        'type': 'number',
        'title': 'Key Size',
        'default': 2048,
        'minimum': 1024,
        'maximum': 8192,
        'description': 'Key Size Bits'
    }
}