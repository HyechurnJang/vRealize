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

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # delete resource
    zoneLink = '/provisioning/resources/placement-zones/' + inputs['id']
    
    for stgProf in vra.get("/provisioning/uerp/provisioning/mgmt/flat-storage-profile?$filter=(placementZoneLink eq '" + zoneLink + "')").raise_for_status().json():
        vra.delete('/provisioning/uerp' + stgProf['documentSelfLink']).raise_for_status()
    
    netProfs = vra.get("/provisioning/uerp/provisioning/resources/network-profiles?expand&$filter=(placementZoneLink eq '" + zoneLink + "')").raise_for_status().json()
    for netProfLink in netProfs['documentLinks']:
        for subnetLink in netProfs['documents'][netProfLink]['subnetLinks']:
            for subnetRangeLink in vra.get("/provisioning/uerp/resources/subnet-ranges?$filter=(subnetLink eq '" + subnetLink + "')").raise_for_status().json()['documentLinks']:
                for ipAddressLink in vra.get("/provisioning/uerp/resources/ip-addresses?$filter=(subnetRangeLink eq '" + subnetRangeLink + "')").raise_for_status().json()['documentLinks']:
                    vra.delete('/provisioning/uerp' + ipAddressLink)
        vra.delete('/provisioning/uerp' + netProfLink).raise_for_status()
        
    vra.delete('/provisioning/uerp' + zoneLink).raise_for_status()
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    return outputs

from importPost import *