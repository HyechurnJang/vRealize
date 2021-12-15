# -*- coding: utf-8 -*-
'''
Created on 2021. 11. 1.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

#===============================================================================
# Rest SDK Abstractions                                                        #
#===============================================================================
class Response: pass
class requests: pass
class VraManager: pass

#===============================================================================
# ABX Code Implementations                                                     #
#===============================================================================
# Import Libraries Here
import json

def handler(context, inputs):
    outputs = {}
    vra = VraManager(context, inputs)
    res = vra.get('/iaas/api/machines')
    print(json.dumps(res, indent=2))
    return outputs

#===============================================================================
# Rest SDK Implementation                                                      #
#===============================================================================
import ssl
import json as JSON
import typing
import urllib.error
import urllib.request
from email.message import Message

class Response(typing.NamedTuple):
    text: str
    headers: Message
    status: int
    def json(self) -> typing.Any:
        try: output = JSON.loads(self.text)
        except JSON.JSONDecodeError: output = ''
        return output

class requests:
    @classmethod
    def __headers__(cls, headers):
        headers = headers or {}
        if 'Accept' not in headers: headers['Accept'] = 'application/json'
        if 'Content-Type' not in headers: headers['Content-Type'] = 'application/json'
        return headers
    @classmethod
    def __payload__(cls, data, json):
        if data: return data.encode('utf-8')
        elif json: return JSON.dumps(json).encode('utf-8')
        else: return ''.encode('utf-8')
    @classmethod
    def __call__(cls, httprequest):
        try:
            with urllib.request.urlopen(httprequest, context=ssl._create_unverified_context()) as httpresponse: response = Response(text=httpresponse.read().decode(httpresponse.headers.get_content_charset('utf-8')), headers=httpresponse.headers, status=httpresponse.status)
        except urllib.error.HTTPError as e: response = Response(text=str(e.reason), headers=e.headers, status=e.code)
        return response
    @classmethod
    def get(cls, url:str, headers:dict=None) -> Response: return cls.__call__(urllib.request.Request(url, method='GET', headers=cls.__headers__(headers)))
    @classmethod
    def post(cls, url:str, headers:dict=None, data:str=None, json:dict=None) -> Response: return cls.__call__(urllib.request.Request(url, method='POST', headers=cls.__headers__(headers), data=cls.__payload__(data, json)))
    @classmethod
    def put(cls, url:str, headers:dict=None, data:str=None, json:dict=None) -> Response: return cls.__call__(urllib.request.Request(url, method='PUT', headers=cls.__headers__(headers), data=cls.__payload__(data, json)))
    @classmethod
    def patch(cls, url:str, headers:dict=None, data:str=None, json:dict=None) -> Response: return cls.__call__(urllib.request.Request(url, method='PATCH', headers=cls.__headers__(headers), data=cls.__payload__(data, json)))
    @classmethod
    def delete(cls, url:str, headers:dict=None) -> Response: return cls.__call__(urllib.request.Request(url, method='DELETE', headers=cls.__headers__(headers)))

class VraManager:
    def __init__(self, context, inputs):
        self.hostname = context.getSecret(inputs['VraManager']['hostname'])
        self.headers = {}
        res = self.post('/csp/gateway/am/api/login?access_token', {'username': context.getSecret(inputs['VraManager']['username']), 'password': context.getSecret(inputs['VraManager']['password'])})
        res = self.post('/iaas/api/login', {'refreshToken': res['refresh_token']})
        self.headers['Authorization'] = 'Bearer ' + res['token']
    def get(self, url:str): return requests.get('https://{}{}'.format(self.hostname, url), headers=self.headers).json()
    def post(self, url:str, data:dict=None): return requests.post('https://{}{}'.format(self.hostname, url), headers=self.headers, json=data).json()
    def put(self, url:str, data:dict=None): return requests.put('https://{}{}'.format(self.hostname, url), headers=self.headers, json=data).json()
    def patch(self, url:str, data:dict=None): return requests.patch('https://{}{}'.format(self.hostname, url), headers=self.headers, json=data).json()
    def delete(self, url:str): return requests.delete('https://{}{}'.format(self.hostname, url), headers=self.headers).json()