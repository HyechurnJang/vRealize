# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

from importPrev import * 

#===============================================================================
# ABX Code Implementations                                                     #
#===============================================================================
# Import Libraries Here
import json
import uuid

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # set default values
    if 'name' not in inputs or inputs['name'] == None or inputs['name'] == '': raise Exception('name property must be required') # Required
    if 'computes' not in inputs or inputs['computes'] == None or inputs['computes'] == '' or not isinstance(inputs['computes'], list) or len(inputs['computes']) == 0: raise Exception('computes property must be required') # Required
    if 'networks' not in inputs or inputs['networks'] == None or inputs['networks'] == '' or not isinstance(inputs['networks'], list) or len(inputs['networks']) == 0: raise Exception('networks property must be required') # Required
    if 'storage' not in inputs or inputs['storage'] == None or inputs['storage'] == '': raise Exception('storage property must be required') # Required
    if 'folder' not in inputs or inputs['folder'] == None or inputs['folder'] == '': inputs['folder'] = '' # Initialized
    if 'placementPolicy' not in inputs or inputs['placementPolicy'] == None or inputs['placementPolicy'] == '': inputs['placementPolicy'] = 'default' # Initialized
    inputs['placementPolicy'] = inputs['placementPolicy'].upper()
    if inputs['placementPolicy'] not in ['DEFAULT', 'BINPACK', 'SPREAD']: raise Exception('placementPolicy property must be set "DEFAULT", "BINPACK" or "SPREAD"')
    if 'loadBalancers' not in inputs or inputs['loadBalancers'] == None or inputs['loadBalancers'] == '' or not isinstance(inputs['loadBalancers'], list): inputs['loadBalancers'] = [] # Initialized
    if 'edgeCluster' not in inputs or inputs['edgeCluster'] == None or inputs['edgeCluster'] == '': inputs['edgeCluster'] = '' # Initialized
    if 'storageType' not in inputs or inputs['storageType'] == None or inputs['storageType'] == '': inputs['storageType'] = 'thin' # Initialized
    if inputs['storageType'] not in ['thin', 'thick', 'eagerZeroedThick']: raise Exception('storageType property must be set "thin", "thick" or "eagerZeroedThick"')
    
    name = inputs['name']
    computes = inputs['computes']
    networks = inputs['networks']
    storage = inputs['storage']
    folder = inputs['folder']
    placementPolicy = inputs['placementPolicy']
    loadBalancers = inputs['loadBalancers']
    edgeCluster = inputs['edgeCluster']
    storageType = inputs['storageType']
    
    # create resource
    ## make computes references
    regions = vra.get('/iaas/api/regions').raise_for_status().json()['content']
    fabricComputes = vra.get("/provisioning/uerp/resources/compute?expand&$filter=((type eq 'ZONE') or (type eq 'VM_HOST'))").raise_for_status().json()['documents'].values()
    computeUerps = []
    computeLinks = []
    for compute in computes:
        for fabricCompute in fabricComputes:
            if compute == fabricCompute['name']:
                if len(computeUerps) == 0:
                    cloudAccountId = fabricCompute['endpointLink'].split('/endpoints/')[1]
                    regionId = fabricCompute['regionId']
                    for region in regions:
                        if region['cloudAccountId'] == cloudAccountId and region['externalRegionId'] == regionId:
                            provisioningRegionLink = '/provisioning/resources/provisioning-regions/' + region['id']
                            break
                    else: raise Exception('could not find region')
                else:
                    if cloudAccountId != fabricCompute['endpointLink'].split('/endpoints/')[1] and regionId != fabricCompute['regionId']: raise Exception('regions of computes are not same')
                computeUerps.append(fabricCompute)
                computeLinks.append(fabricCompute['documentSelfLink'])
                break
        else: raise Exception('could not find compute : ' + compute)
    computes = computeUerps
    
    ## make networks references
    subnets = []
    subnetLinks = []
    for network in networks:
        try: network = vra.get('/provisioning/uerp' + network).raise_for_status().json()
        except: raise Exception('could not find network : ' + network)
        try: subnets.append(vra.get('/provisioning/uerp' + network['subnetLink']).raise_for_status().json())
        except: raise Exception('could not find subnet : ' + network['subnetLink'])
        subnetLinks.append(network['subnetLink'])
    
    ## make loadbalancer references
    loadBalancerUerps = []
    loadBalancerLinks = []
    for loadBalancer in loadBalancers:
        loadBalancerLinks.append(loadBalancer)
        try: loadBalancerUerps.append(vra.get('/provisioning/uerp' + loadBalancer).raise_for_status().json())
        except: raise Exception('could not find load balancer : ' + loadBalancer)
    loadBalancers = loadBalancerUerps
    
    ## make edge cluster references
    edgeClusterRouterStateLink = None
    if edgeCluster:
        edgeClusterRouterStateLink = vra.get("/provisioning/uerp/resources/routers?$filter=(name eq '" + edgeCluster + "')").raise_for_status().json()
        if edgeClusterRouterStateLink['totalCount'] == 1: edgeClusterRouterStateLink = edgeClusterRouterStateLink['documentLinks'][0]
        else: raise Exception('could not find edge cluster : ' + edgeCluster)
    
    ## make storage reference
    storageDescription = vra.get("/provisioning/uerp/resources/storage-descriptions?expand&$filter=((name eq '" + storage + "') and (endpointLink eq '/resources/endpoints/" + cloudAccountId + "') and (regionId eq '" + regionId + "'))").raise_for_status().json()
    if storageDescription['totalCount'] == 1: storageDescription = storageDescription['documents'][storageDescription['documentLinks'][0]]
    else: raise Exception('could not find storage : ' + storage)
    storageDescriptionLink = storageDescription['documentSelfLink']
    
    ## create zone
    zone = vra.post('/provisioning/uerp/provisioning/resources/placement-zones?expand', {
        'name': name,
        'type': 'vpc',
        'provisioningRegionLink': provisioningRegionLink,
        'computes': computes,
        'computeLinks': computeLinks,
        'placementPolicy': placementPolicy,
        'isStatic': True,
        'customProperties': {'resourceGroupName': folder}
    }).raise_for_status().json()
    placementZoneLink = zone['documentSelfLink']
    
    vra.post('/provisioning/uerp/provisioning/resources/network-profiles', {
        'name': 'vpc-' + name + '-' + str(uuid.uuid4()),
        'provisioningRegionLink': provisioningRegionLink,
        'placementZoneLink': placementZoneLink,
        'subnets': subnets,
        'subnetLinks': subnetLinks,
        'loadBalancers': loadBalancers,
        'loadBalancerLinks': loadBalancerLinks,
        'securityGroups': [],
        'securityGroupLinks': [],
        'isolationType': 'NONE',
        'isolationNetworkLink': None,
        'isolatedSubnetCIDRPrefix': None,
        'isolationNetworkCIDR': None,
        'isolationNetwork': {},
        'customProperties': {
            'edgeClusterRouterStateLink': edgeClusterRouterStateLink,
            'onDemandNetworkIPAssignmentType': 'static',
            'tier0LogicalRouterStateLink': None,
            'distributedLogicalRouterStateLink': None,
            'datacenterId': regionId,
            'resourcePoolId': None,
            'dataStoreId': None
        }
    }).raise_for_status().json()
    
    vra.post('/provisioning/uerp/provisioning/mgmt/flat-storage-profile', {
        'provisioningRegionLink': provisioningRegionLink,
        'placementZoneLink': placementZoneLink,
        'storageDescription': storageDescription,
        'storageDescriptionLink': storageDescriptionLink,
        'customProperties': {'provisioningType': storageType}
    }).raise_for_status().json()
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['id'] = placementZoneLink.split('/placement-zones/')[1]
    return outputs

from importPost import *