#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 10:35:32 2017

@author: steven
"""

import requests

#import json
import jwt
import time

import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
jsonpickle_numpy.register_handlers()


#from requests_jwt import JWTAuth

#payload = {'key1': 'value1', 'key2': 'value2'}
#
#>>> r = requests.post("http://httpbin.org/post", data=payload)

class AuthenticationError(Exception):
    pass
    
class Client:
    def __init__(self,username,password):
        self.username=username
        self.password=password
        self.token=None
        self.token_exp=0.
#        self.token_nbf=time.time()
    def _get_auth_header(self):
        if self.token_exp<time.time():
            print('Token expired, reauth')
            # Authenticate
            r = requests.post('https://api.software.dessia.tech/auth', json={"username": self.username,"password":self.password})
            print(r)
            if r.status_code==200:
                self.token=r.json()['access_token']
                self.token_exp=jwt.decode(self.token,verify=False)['exp']
                print('Auth in {}s'.format(r.elapsed.total_seconds()))
            else:
                raise AuthenticationError
                
        auth_header={'Authorization':'JWT {}'.format(self.token)}
        return auth_header
    
    auth_header=property(_get_auth_header)
    
        
    def MyAccount(self):
        r=requests.get('https://api.software.dessia.tech/myaccount',headers=self.auth_header)
        return r
    
    def TransactionDetails(self,transaction_id):
        r=requests.get('https://api.software.dessia.tech/transactions/{}'.format(transaction_id),
                       headers=self.auth_header)
        return r
    
    def AddTransaction(self,debitor_id,creditor_id,amount,infos):
        data={'debitor_id':debitor_id,'creditor_id':creditor_id,'amount':amount,'infos':infos}
        r=requests.post('https://api.software.dessia.tech/transactions/add',
                       headers=self.auth_header,data=data)
        return r
    
    def Model3DResultsKeys(self):
        r=requests.get('https://api.software.dessia.tech/powertransmission/database/model3d_results/keys',headers=self.auth_header)
        return r
        
    def AddModel3DResult(self,result,name,infos):
        data={'result':jsonpickle.encode(result,keys=True),'name':name,'infos':infos}
        r=requests.post('https://api.software.dessia.tech/powertransmission/database/model3d_result/add',headers=self.auth_header,data=data)
        return r
    
    def GetModel3DResult(self,id_result):
        r=requests.get('https://api.software.dessia.tech/powertransmission/database/model3d_result/object/{}'.format(id_result),headers=self.auth_header)
        if r.status_code==200:
            return jsonpickle.decode(r.text,keys=True)
        else:
            return r
    
    def GetModel3DTextReport(self,id_result):
        r=requests.get('https://api.software.dessia.tech/powertransmission/database/model3d_result/text_report/{}'.format(id_result),headers=self.auth_header)
        return r
        
    def SubmitModel3DOptimization(self,model3d,bounds_sl):
        data={'model3d_optimizer':jsonpickle.encode(model3d,keys=True),
              'bounds_shaft_lines':jsonpickle.encode(bounds_sl,keys=True),
              'infos':''}
        r=requests.post('https://api.software.dessia.tech/powertransmission/jobs/optimization3d/submit',headers=self.auth_header,data=data)
        return r
        
    def JobDetails(self,id_job):
        r=requests.get('https://api.software.dessia.tech/jobs/infos/{}'.format(id_job),headers=self.auth_header)
        return r

