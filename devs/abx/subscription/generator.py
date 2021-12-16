# -*- coding: utf-8 -*-
'''
Created on 2021. 12. 15.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

#===============================================================================
# Generator Settings
#===============================================================================
installerName = 'vraPackageInstaller'

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

actions = [
    #===========================================================================
    'change_name'
    #===========================================================================
]

#===============================================================================
# Generator Running
#===============================================================================
import os
import re
import json
import shutil
import zipfile
import datetime

REGEX = r'# __ABX_IMPLEMENTATIONS_START__[\r\n]+(?P<text>[\W\w\r\n]+)[\r\n]+# __ABX_IMPLEMENTATIONS_END__'

TEXTILE = '''
_NEWLINE_ = '\\\\n'
'''

with open('common/installer.py', 'r') as fd: installer = re.findall(REGEX, fd.read())[0]

descriptions = {}
for action in actions:
    manifest = __import__('actions.{}.manifest'.format(action)).__getattribute__(action).manifest
    desc = {
        'inputs': manifest.inputs,
    }
    with open('common/{}.py'.format(manifest.sdk), 'r') as fd: desc['sdk'] = re.findall(REGEX, fd.read())[0]
    with open('actions/{}/action.py'.format(action), 'r') as fd: desc['handler'] = re.findall(REGEX, fd.read())[0]
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
    'sdk': '''%s\n%s''',
    'handler': '''%s'''
""" % (
    name,
    desc['inputs'],
    desc['sdk'],
    TEXTILE,
    desc['handler']))
    fd.write('}\n')
    
    # write installer
    fd.write('''
%s
''' % (installer))

    # copy installer latest
    shutil.copy('dist/{}/{}_{}.py'.format(installerName, installerName, tstamp), 'dist/latest.py')

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
