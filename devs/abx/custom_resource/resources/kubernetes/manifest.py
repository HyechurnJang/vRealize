# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

name = 'Kubernetes' # custom resource name

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
    'name': {
        'type': 'string',
        'title': 'Name',
        'description': 'Kubernetes Cluster Name'
    },
    'clusterType': {
        'type': 'string',
        'title': 'Cluster Type',
        'enum': ['tanzu', 'external'],
        'description': 'Registered Kubernetes Type'
    },
    'cluster': {
        'type': 'string',
        'title': 'Cluster ID',
        'default': '',
        'description': 'Cluster ID in CMX Registered'
    },
    'project': {
        'type': 'string',
        'title': 'Project Name',
        'default': '',
        'description': 'Allocated Project Name of External Cluster'
    },
    'kubeConfig': {
        'type': 'string',
        'title': 'Kubernetes Config',
        'default': '',
        'description': 'Kube-Config of External Cluster'
    },
    'clusterManifest': {
        'type': 'string',
        'title': 'Cluster Manifest',
        'default': '',
        'description': 'Manifest for Initial Cluster Config'
    }
}