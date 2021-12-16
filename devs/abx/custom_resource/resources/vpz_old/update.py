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
    # # set common values
    # vra = VraManager(context, inputs)
    #
    # # retrieve resource
    # resource = vra.get('' + inputs['id'])
    # try: resource = resource.raise_for_status().json()
    # except Exception as e:
    #     try: errMsg = json.loads(resource.json()['message'])['serverMessage']
    #     except: raise e
    #     else: raise Exception(errMsg)
    #
    # # update resource
    # if 'var1' in inputs: resource['var1'] = inputs['var1']
    # if 'var2' in inputs: resource['var2'] = inputs['var2']
    # resource = vra.post('' + inputs['id']).raise_for_status().json()
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    return outputs

from importPost import *