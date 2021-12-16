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
_NEWLINE_ = '\n'

# __ABX_IMPLEMENTATIONS_START__
#===============================================================================
# ABX Code Implementations                                                     #
#===============================================================================
# Import Libraries Here
def changeIp2Num(ip):
    num = 0
    for n in ip.split('.'): num = (num << 8) + int(n)
    return num

def changeNum2Ip(num):
    return str(num >> 24) + '.' + str(num >> 16 & 255) + '.' + str(num >> 8 & 255) + '.' + str(num & 255)

def allocateAddress(vra, subnetRangeLink, ipAddress):
    check = vra.get("/provisioning/uerp/resources/ip-addresses?expand&$filter=((subnetRangeLink eq '{}') and (ipAddress eq '{}'))".format(subnetRangeLink, ipAddress))
    totalCount = check['totalCount']
    if totalCount == 0:
        return vra.post('/provisioning/uerp/resources/ip-addresses', {
            'subnetRangeLink': subnetRangeLink,
            'ipAddress': ipAddress,
            'customProperties': {},
            'ipAddressStatus': 'ALLOCATED',
            'connectedResourceLink': 'vra-custom-resource'
        })
    elif totalCount == 1:
        ipAddressLink = check['documentLinks'][0]
        ipAddressObj = check['documents'][ipAddressLink]
        if ipAddressObj['ipAddressStatus'] == 'AVAILABLE':
            ipAddressObj['ipAddressStatus'] = 'ALLOCATED'
            ipAddressObj['connectedResourceLink'] = 'vra-custom-resource'
            return vra.patch('/provisioning/uerp' + ipAddressLink, ipAddressObj)
        else:
            raise Exception('ip address has status of allocated or released')
    else:
        raise Exception('ip addresses are retrieved more 1')

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # set default values
    if 'network' not in inputs or not inputs['network']: raise Exception('network property must be required') # Required
    if 'address' not in inputs: inputs['address'] = None # Optional Init
    
    network = inputs['network']
    address = inputs['address']
    numAddress = changeIp2Num(inputs['address']) if inputs['address'] else 0
    
    # create resource
    computeNetwork = vra.get('/provisioning/uerp' + network)
    for subnetRange in vra.get("/provisioning/uerp/resources/subnet-ranges?expand&$filter=(subnetLink eq '{}')".format(computeNetwork['subnetLink']))['documents'].values():
        subnetRangeLink = subnetRange['documentSelfLink'];
        unAvailable = []
        for ipAddress in vra.get("/provisioning/uerp/resources/ip-addresses?expand&$filter=((subnetRangeLink eq '{}') and (ipAddressStatus ne 'AVAILABLE'))".format(subnetRangeLink))['documents'].values():
            unAvailable.append(changeIp2Num(ipAddress['ipAddress']))
        stt = changeIp2Num(subnetRange['startIPAddress'])
        end = changeIp2Num(subnetRange['endIPAddress'])
        if numAddress > 0:
            if stt <= numAddress and end >= numAddress:
                if numAddress not in unAvailable:
                    resource = allocateAddress(vra, subnetRangeLink, address)
                    break
                else: raise Exception('ip address is already allocated')
        else:
            for numAddress in range(stt, end + 1):
                if numAddress not in unAvailable:
                    inputs['address'] = changeNum2Ip(numAddress)
                    resource = allocateAddress(vra, subnetRangeLink, inputs['address'])
                    break
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['id'] = resource['documentSelfLink'].split('/ip-addresses/')[1]
    return outputs
# __ABX_IMPLEMENTATIONS_END__
