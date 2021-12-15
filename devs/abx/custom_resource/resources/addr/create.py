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

def changeIp2Num(ip):
    num = 0
    for n in ip.split('.'): num = (num << 8) + int(n)
    return num

def changeNum2Ip(num):
    return str(num >> 24) + '.' + str(num >> 16 & 255) + '.' + str(num >> 8 & 255) + '.' + str(num & 255)

def allocateAddress(vra, subnetRangeLink, ipAddress):
    check = vra.get("/provisioning/uerp/resources/ip-addresses?expand&$filter=((subnetRangeLink eq '" + subnetRangeLink + "') and (ipAddress eq '" + ipAddress + "'))").raise_for_status().json()
    totalCount = check['totalCount']
    if totalCount == 0:
        return vra.post('/provisioning/uerp/resources/ip-addresses', {
            'subnetRangeLink': subnetRangeLink,
            'ipAddress': ipAddress,
            'customProperties': {},
            'ipAddressStatus': 'ALLOCATED',
            'connectedResourceLink': 'vra-custom-resource'
        }).raise_for_status().json()
    elif totalCount == 1:
        ipAddressLink = check['documentLinks'][0]
        ipAddressObj = check['documents'][ipAddressLink]
        if ipAddressObj['ipAddressStatus'] == 'AVAILABLE':
            ipAddressObj['ipAddressStatus'] = 'ALLOCATED'
            ipAddressObj['connectedResourceLink'] = 'vra-custom-resource'
            return vra.patch('/provisioning/uerp' + ipAddressLink, ipAddressObj).raise_for_status().json()
        else:
            raise Exception('ip address has status of allocated or released')
    else:
        raise Exception('ip addresses are retrieved more 1')

# Implement Handler Here
def handler(context, inputs):
    # set common values
    vra = VraManager(context, inputs)
    
    # set default values
    if 'network' not in inputs or inputs['network'] == None or inputs['network'] == '': raise Exception('network property must be required')
    if 'address' not in inputs or inputs['address'] == None or inputs['address'] == '': inputs['address'] = None
    numAddress = changeIp2Num(inputs['address']) if inputs['address'] else 0
    
    # create resource
    computeNetwork = vra.get('/provisioning/uerp' + inputs['network']).raise_for_status().json()
    for subnetRange in vra.get("/provisioning/uerp/resources/subnet-ranges?expand&$filter=(subnetLink eq '" + computeNetwork['subnetLink'] + "')").raise_for_status().json()['documents'].values():
        subnetRangeLink = subnetRange['documentSelfLink'];
        unAvailable = []
        for address in vra.get("/provisioning/uerp/resources/ip-addresses?expand&$filter=((subnetRangeLink eq '" + subnetRangeLink + "') and (ipAddressStatus ne 'AVAILABLE'))").raise_for_status().json()['documents'].values():
            unAvailable.append(changeIp2Num(address['ipAddress']))
        stt = changeIp2Num(subnetRange['startIPAddress'])
        end = changeIp2Num(subnetRange['endIPAddress'])
        if numAddress > 0:
            if stt <= numAddress and end >= numAddress:
                if numAddress not in unAvailable:
                    result = allocateAddress(vra, subnetRangeLink, inputs['address'])
                    break
                else: raise Exception('ip address is already allocated')
        else:
            for numAddress in range(stt, end + 1):
                if numAddress not in unAvailable:
                    inputs['address'] = changeNum2Ip(numAddress)
                    result = allocateAddress(vra, subnetRangeLink, inputs['address'])
                    break
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['id'] = result['documentSelfLink'].split('/ip-addresses/')[1]
    return outputs
    

from importPost import *