# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

name = 'VirtualPrivateZone' # custom resource name

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
        'description': 'Name of virtual private zone'
    },
    'computes': {
        'type': 'array',
        'title': 'Computes',
        'items': {
            'type': 'string'
        },
        'description': 'Compute name list of placement hosts, clusters or resource pools'
    },
    'networks': {
        'type': 'array',
        'title': 'Networks',
        'items': {
            'type': 'string'
        },
        'description': 'Network id list'
    },
    'storage': {
        'type': 'string',
        'title': 'Storage',
        'description': 'Datastore name to deploy',
    },
    'folder': {
        'type': 'string',
        'title': 'Folder',
        'default': '',
        'description': 'Folder name to deploy',
    },
    'placementPolicy': {
        'type': 'string',
        'title': 'Placement Policy',
        'default': 'default',
        'enum': ['default', 'binpack', 'spread'],
        'description': 'Placement policy with "default", "binpack" or "spread"'
    },
    'loadBalancers': {
        'type': 'array',
        'title': 'Load Balancer',
        'default': [],
        'items': {
            'type': 'string'
        },
        'description': 'Load balancer id list'
    },
    'edgeCluster': {
        'type': 'string',
        'title': 'Edge Cluster',
        'default': '',
        'description': 'Edge cluster name to use deployment',
    },
    'storageType': {
        'type': 'string',
        'title': 'Storage Type',
        'default': 'thin',
        'enum': ['thin', 'thick', 'eagerZeroedThick'],
        'description': 'Storage type with "thin", "thick" or "eagerZeroedThick"'
    },
}