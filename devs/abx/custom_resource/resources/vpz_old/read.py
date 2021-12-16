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
    # bypass resource
    outputs = inputs
    outputs.pop('VraManager')
    return outputs

from importPost import *