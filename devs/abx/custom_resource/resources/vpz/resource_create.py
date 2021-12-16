# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

import sys
import importlib
import manifest
sys.path.insert(0, '../../common')
_module = importlib.import_module(manifest.sdk)
for exportObject in _module.exportObjects: __builtins__[exportObject] = _module.__getattribute__(exportObject)

# __ABX_IMPLEMENTATIONS_START__
#===============================================================================
# ABX Code Implementations                                                     #
#===============================================================================
# Import Libraries Here
import uuid

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # set default values
    if 'name' not in inputs or not inputs['name']: raise Exception('name property must be required') # Required
    if 'computes' not in inputs or not inputs['computes']: raise Exception('computes property must be required') # Required
    if 'networks' not in inputs or not inputs['networks']: raise Exception('networks property must be required') # Required
    if 'storage' not in inputs or not inputs['storage']: raise Exception('storage property must be required') # Required
    if 'placementPolicy' not in inputs or not inputs['placementPolicy']: inputs['placementPolicy'] = 'default' # Optional Init
    if 'loadBalancers' not in inputs: inputs['loadBalancers'] = [] # Optional Init
    if 'edgeCluster' not in inputs: inputs['edgeCluster'] = '' # Optional Init
    if 'storageType' not in inputs or not inputs['storageType']: inputs['storageType'] = 'thin' # Optional Init
    
    name = inputs['name']
    computes = inputs['computes']
    networks = inputs['networks']
    storage = inputs['storage']
    folder = inputs['folder']
    placementPolicy = inputs['placementPolicy'].upper()
    loadBalancers = inputs['loadBalancers']
    edgeCluster = inputs['edgeCluster']
    storageType = inputs['storageType']
    
    # create resource
    ## make computes references
    regions = vra.get('/iaas/api/regions')['content']
    fabricComputes = vra.get("/provisioning/uerp/resources/compute?expand&$filter=((type eq 'ZONE') or (type eq 'VM_HOST'))")['documents'].values()
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
        try: network = vra.get('/provisioning/uerp' + network)
        except: raise Exception('could not find network : ' + network)
        try: subnets.append(vra.get('/provisioning/uerp' + network['subnetLink']))
        except: raise Exception('could not find subnet : ' + network['subnetLink'])
        subnetLinks.append(network['subnetLink'])
    
    ## make loadbalancer references
    loadBalancerUerps = []
    loadBalancerLinks = []
    for loadBalancer in loadBalancers:
        loadBalancerLinks.append(loadBalancer)
        try: loadBalancerUerps.append(vra.get('/provisioning/uerp' + loadBalancer))
        except: raise Exception('could not find load balancer : ' + loadBalancer)
    loadBalancers = loadBalancerUerps
    
    ## make edge cluster references
    edgeClusterRouterStateLink = None
    if edgeCluster:
        edgeClusterRouterStateLink = vra.get("/provisioning/uerp/resources/routers?$filter=(name eq '{}')".format(edgeCluster))
        if edgeClusterRouterStateLink['totalCount'] == 1: edgeClusterRouterStateLink = edgeClusterRouterStateLink['documentLinks'][0]
        else: raise Exception('could not find edge cluster : ' + edgeCluster)
    
    ## make storage reference
    storageDescription = vra.get("/provisioning/uerp/resources/storage-descriptions?expand&$filter=((name eq '{}') and (endpointLink eq '/resources/endpoints/{}') and (regionId eq '{}'))".format(storage, cloudAccountId, regionId))
    if storageDescription['totalCount'] == 1: storageDescription = storageDescription['documents'][storageDescription['documentLinks'][0]]
    else: raise Exception('could not find storage : ' + storage)
    storageDescriptionLink = storageDescription['documentSelfLink']
    
    ## create zone
    resource = vra.post('/provisioning/uerp/provisioning/resources/placement-zones?expand', {
        'name': name,
        'type': 'vpc',
        'provisioningRegionLink': provisioningRegionLink,
        'computes': computes,
        'computeLinks': computeLinks,
        'placementPolicy': placementPolicy,
        'isStatic': True,
        'customProperties': {'resourceGroupName': folder}
    })
    placementZoneLink = resource['documentSelfLink']
    
    ## create network profile
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
    })
    
    ## create storage profile
    vra.post('/provisioning/uerp/provisioning/mgmt/flat-storage-profile', {
        'provisioningRegionLink': provisioningRegionLink,
        'placementZoneLink': placementZoneLink,
        'storageDescription': storageDescription,
        'storageDescriptionLink': storageDescriptionLink,
        'customProperties': {'provisioningType': storageType}
    })
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['id'] = placementZoneLink.split('/placement-zones/')[1]
    return outputs
# __ABX_IMPLEMENTATIONS_END__
