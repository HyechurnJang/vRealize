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
    if 'var1' not in inputs or inputs['var1'] == None or inputs['var1'] == '': raise Exception('var1 property must be required') # Required
    if 'var2' not in inputs or inputs['var2'] == None or inputs['var2'] == '': inputs['var2'] = None # Initialized
    
    # create resource
    resource = vra.post('')
    
    # publish resource
    outputs = inputs
    outputs.pop('VraManager')
    outputs['id'] = resource['id']
    return outputs
# __ABX_IMPLEMENTATIONS_END__
