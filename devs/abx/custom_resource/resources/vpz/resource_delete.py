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
    
    # delete resource
    zoneLink = '/provisioning/resources/placement-zones/' + inputs['id']
    
    for stgProf in vra.get("/provisioning/uerp/provisioning/mgmt/flat-storage-profile?$filter=(placementZoneLink eq '{}')".format(zoneLink)):
        vra.delete('/provisioning/uerp' + stgProf['documentSelfLink'])
    
    netProfs = vra.get("/provisioning/uerp/provisioning/resources/network-profiles?expand&$filter=(placementZoneLink eq '{}')".format(zoneLink))
    for netProfLink in netProfs['documentLinks']:
        for subnetLink in netProfs['documents'][netProfLink]['subnetLinks']:
            for subnetRangeLink in vra.get("/provisioning/uerp/resources/subnet-ranges?$filter=(subnetLink eq '{}')".format(subnetLink))['documentLinks']:
                for ipAddressLink in vra.get("/provisioning/uerp/resources/ip-addresses?$filter=(subnetRangeLink eq '{}')".format(subnetRangeLink))['documentLinks']:
                    vra.delete('/provisioning/uerp' + ipAddressLink)
        vra.delete('/provisioning/uerp' + netProfLink)
        
    vra.delete('/provisioning/uerp' + zoneLink)
    
    # publish null resource
    return {}
# __ABX_IMPLEMENTATIONS_END__
