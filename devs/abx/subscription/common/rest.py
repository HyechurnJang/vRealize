# -*- coding: utf-8 -*-
'''
Created on 1983. 08. 09.
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

exportObjects = ['Response', 'requests']

# __ABX_IMPLEMENTATIONS_START__
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
    def raise_for_status(self):
        if self.status >= 400: raise Exception('response error with status code {}'.format(self.status))
        return self

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
    def __encode__(cls, url): return url.replace(' ', '%20').replace('$', '%24').replace("'", '%27').replace('[', '%5B').replace(']', '%5D')
    @classmethod
    def __call__(cls, httprequest):
        try:
            with urllib.request.urlopen(httprequest, context=ssl._create_unverified_context()) as httpresponse: response = Response(text=httpresponse.read().decode(httpresponse.headers.get_content_charset('utf-8')), headers=httpresponse.headers, status=httpresponse.status)
        except urllib.error.HTTPError as e: response = Response(text=e.fp.read().decode('utf-8'), headers=e.headers, status=e.code)
        return response
    @classmethod
    def get(cls, url:str, headers:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='GET', headers=cls.__headers__(headers)))
    @classmethod
    def post(cls, url:str, headers:dict=None, data:str=None, json:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='POST', headers=cls.__headers__(headers), data=cls.__payload__(data, json)))
    @classmethod
    def put(cls, url:str, headers:dict=None, data:str=None, json:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='PUT', headers=cls.__headers__(headers), data=cls.__payload__(data, json)))
    @classmethod
    def patch(cls, url:str, headers:dict=None, data:str=None, json:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='PATCH', headers=cls.__headers__(headers), data=cls.__payload__(data, json)))
    @classmethod
    def delete(cls, url:str, headers:dict=None) -> Response: return cls.__call__(urllib.request.Request(cls.__encode__(url), method='DELETE', headers=cls.__headers__(headers)))
# __ABX_IMPLEMENTATIONS_END__
