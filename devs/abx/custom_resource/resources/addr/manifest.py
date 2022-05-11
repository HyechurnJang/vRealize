# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

name = 'Address' # custom resource name

sdk = 'vra' # imported SDK at common directory

inputs = {
    'create': {
        'VraManager': 'constant'
    },
    'read': {
    },
    'update': {
    },
    'delete': {
        'VraManager': 'constant'
    }
}

properties = {
    'network': {
        'type': 'string',
        'title': 'Network',
        'recreateOnUpdate': True,
        'description': 'Network id for ip allocation',
    },
    'address': {
        'type': 'string',
        'title': 'Address',
        'default': '',
        'recreateOnUpdate': True,
        'description': 'Network address specified',
    },
}