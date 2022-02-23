# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

name = 'Cert' # custom resource name

sdk = 'no' # imported SDK at common directory

inputs = {
    'create': {
    },
    'read': {
    },
    'update': {
    },
    'delete': {
    }
}

properties = {
    'keySize': {
        'type': 'number',
        'title': 'Key Size',
        'default': 2048,
        'description': 'RSA Key Size'
    }
}