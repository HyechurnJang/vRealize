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
    if 'loadBalancers' not in inputs or not inputs['loadBalancers']: inputs['loadBalancers'] = [] # Optional Init
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
    
    # retrieve resource
    ## retrieve computes references
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
    
    ## retrieve networks references
    subnets = []
    subnetLinks = []
    for network in networks:
        try: network = vra.get('/provisioning/uerp' + network)
        except: raise Exception('could not find network : ' + network)
        try: subnets.append(vra.get('/provisioning/uerp' + network['subnetLink']))
        except: raise Exception('could not find subnet : ' + network['subnetLink'])
        subnetLinks.append(network['subnetLink'])
    
    ## retrieve loadbalancer references
    loadBalancerUerps = []
    loadBalancerLinks = []
    for loadBalancer in loadBalancers:
        loadBalancerLinks.append(loadBalancer)
        try: loadBalancerUerps.append(vra.get('/provisioning/uerp' + loadBalancer))
        except: raise Exception('could not find load balancer : ' + loadBalancer)
    loadBalancers = loadBalancerUerps
    
    ## retrieve edge cluster references
    edgeClusterRouterStateLink = None
    if edgeCluster:
        edgeClusterRouterStateLink = vra.get("/provisioning/uerp/resources/routers?$filter=(name eq '{}')".format(edgeCluster))
        if edgeClusterRouterStateLink['totalCount'] == 1: edgeClusterRouterStateLink = edgeClusterRouterStateLink['documentLinks'][0]
        else: raise Exception('could not find edge cluster : ' + edgeCluster)
    
    ## retrieve storage reference
    storageDescription = vra.get("/provisioning/uerp/resources/storage-descriptions?expand&$filter=((name eq '{}') and (endpointLink eq '/resources/endpoints/{}') and (regionId eq '{}'))".format(storage, cloudAccountId, regionId))
    if storageDescription['totalCount'] == 1: storageDescription = storageDescription['documents'][storageDescription['documentLinks'][0]]
    else: raise Exception('could not find storage : ' + storage)
    storageDescriptionLink = storageDescription['documentSelfLink']
    
    # update resource
    ## update zone profile
    zoneLink = '/provisioning/resources/placement-zones/' + inputs['id']
    zoneProf = vra.get('/provisioning/uerp' + zoneLink)
    zoneProf['name'] = name
    zoneProf['provisioningRegionLink'] = provisioningRegionLink
    zoneProf['computes'] = computes
    zoneProf['computeLinks'] = computeLinks
    zoneProf['placementPolicy'] = placementPolicy
    zoneProf['customProperties']['resourceGroupName'] = folder
    zoneProf = vra.put('/provisioning/uerp' + zoneLink, zoneProf)
    placementZoneLink = zoneProf['documentSelfLink']
    
    ## update network profile
    netProf = vra.get("/provisioning/uerp/provisioning/resources/network-profiles?expand&$filter=(placementZoneLink eq '{}')".format(placementZoneLink))
    if len(netProf['documentLinks']) < 1: raise Exception('could not find network profile')
    elif len(netProf['documentLinks']) > 1: raise Exception('multi network profiles are retrieved')
    netProf = netProf['documents'][netProf['documentLinks'][0]]
    netProf['provisioningRegionLink'] = provisioningRegionLink
    netProf['placementZoneLink'] = placementZoneLink
    netProf['subnets'] = subnets
    netProf['subnetLinks'] = subnetLinks
    netProf['loadBalancers'] = loadBalancers
    netProf['loadBalancerLinks'] = loadBalancerLinks
    netProf['customProperties']['edgeClusterRouterStateLink'] = edgeClusterRouterStateLink
    netProf = vra.put('/provisioning/uerp' + netProf['documentSelfLink'], netProf)
    
    ## update storage profile
    stgProf = vra.get("/provisioning/uerp/provisioning/mgmt/flat-storage-profile?$filter=(placementZoneLink eq '{}')".format(placementZoneLink))
    if len(stgProf) != 1: raise Exception('could not find storage profile')
    stgProf = stgProf[0]
    stgProf['provisioningRegionLink'] = provisioningRegionLink
    stgProf['placementZoneLink'] = placementZoneLink
    stgProf['storageDescription'] = storageDescription
    stgProf['storageDescriptionLink'] = storageDescriptionLink
    stgProf['customProperties']['provisioningType'] = storageType
    stgProf = vra.put('/provisioning/uerp' + stgProf['documentSelfLink'], stgProf)
        
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    return outputs
# __ABX_IMPLEMENTATIONS_END__
