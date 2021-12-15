# -*- coding: utf-8 -*-
'''
Created on 2021. 12. 15.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

#===============================================================================
# Generator Settings
#===============================================================================
installerName = 'installer_name_here'

constants = {
    #===========================================================================
    # 'SampleManager': {
    #     'encrypted': True,
    #     'map': {
    #         'sampleHostname': 'hostname',
    #         'sampleUsername': 'username',
    #         'samplePassword': 'password'
    #     }
    # },
    #===========================================================================
}

resources = [
    #===========================================================================
    # 'project',
    # 'deployment',
    # 'vpz',
    # 'addr',
    # 'kubernetes',
    # 'pipeline',
    # 'code',
    # 'script',
    # 'cert',
    # 'data',
    #===========================================================================
]

#===============================================================================
# Generator Running
#===============================================================================
import os
import re
import json
import zipfile
import datetime

REGEX = r'# __ABX_IMPLEMENTATIONS_START__[\r\n]+(?P<text>[\W\w\r\n]+)[\r\n]+# __ABX_IMPLEMENTATIONS_END__'

with open('common/installer.py', 'r') as fd: installer = re.findall(REGEX, fd.read())[0]

descriptions = {}
for resource in resources:
    
    manifest = __import__('resources.{}.manifest'.format(resource)).__getattribute__(resource).manifest
    desc = {
        'inputs': manifest.inputs,
        'properties': manifest.properties,
    }
    with open('common/{}.py'.format(manifest.sdk), 'r') as fd: desc['sdk'] = re.findall(REGEX, fd.read())[0]
    with open('resources/{}/resource_create.py'.format(resource), 'r') as fd: desc['createHandler'] = re.findall(REGEX, fd.read())[0]
    with open('resources/{}/resource_read.py'.format(resource), 'r') as fd: desc['readHandler'] = re.findall(REGEX, fd.read())[0]
    with open('resources/{}/resource_update.py'.format(resource), 'r') as fd: desc['updateHandler'] = re.findall(REGEX, fd.read())[0]
    with open('resources/{}/resource_delete.py'.format(resource), 'r') as fd: desc['deleteHandler'] = re.findall(REGEX, fd.read())[0]
    descriptions[manifest.name] = desc

os.makedirs('dist', exist_ok=True)
os.makedirs('dist/{}'.format(installerName), exist_ok=True)
tstamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

with open('dist/{}/{}_{}.py'.format(installerName, installerName, tstamp), 'w') as fd:
    # write header
    fd.write("""# -*- coding: utf-8 -*-
'''
Created on 2021. 11. 18.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''
""")
    
    # write constant descriptions
    fd.write('''
constDescs = %s
''' % constants)
    
    # write resource descriptions
    fd.write('''
rscDescs = {
''')
    for name, desc in descriptions.items():
        fd.write("""'%s': {
    'inputs': %s,
    'properties': %s,
    'sdk': '''%s''',
    'createHandler': '''%s''',
    'readHandler': '''%s''',
    'deleteHandler': '''%s''',
""" % (
    name,
    desc['inputs'],
    desc['properties'],
    desc['sdk'],
    desc['createHandler'],
    desc['readHandler'],
    desc['deleteHandler']))
        if 'updateHandler' in desc: fd.write("""    'updateHandler': '''%s''',""" % desc['updateHandler'])
        fd.write('''
},
''')
        
    fd.write('}\n')
    
    # write installer
    fd.write('''
%s
''' % (installer))

with open('dist/{}/{}_{}.abx'.format(installerName, installerName, tstamp), 'w') as fd:
    # write manifest
    fd.write('''---
exportVersion: "1"
name: "{}"
runtime: "python"
entrypoint: "handler"
timeoutSeconds: 600
deploymentTimeoutSeconds: 900
actionType: "SCRIPT"
memoryInMB: 300
inputs:
  vraHostname: ""
  vraPassword: ""
  vraUsername: ""
  vraProject: ""
'''.format(installerName))
    
    # write additional constants
    for constant in constants.values():
        for key in constant['map'].keys():
            fd.write('  {}: ""\n'.format(key))

with zipfile.ZipFile('dist/{}/{}_{}.zip'.format(installerName, installerName, tstamp), 'w') as fd:
    fd.write('dist/{}/{}_{}.abx'.format(installerName, installerName, tstamp), '{}.abx'.format(installerName))
    fd.write('dist/{}/{}_{}.py'.format(installerName, installerName, tstamp), '{}.py'.format(installerName))
