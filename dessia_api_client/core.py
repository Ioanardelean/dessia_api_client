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


class AuthenticationError(Exception):
    pass
    
class Client:
    def __init__(self,email=None,password=None):
        if email is None:
            email=input('email for DessIA API:')
        if password is None:
            password=input('Password for DessIA API:')
        self.email=email
        self.password=password
        self.token=None
        self.token_exp=0.
#        self.token_nbf=time.time()
    def _get_auth_header(self):
        if self.token_exp<time.time():
            print('Token expired, reauth')
            # Authenticate
            r = requests.post('https://api.software.dessia.tech/auth', json={"email": self.email,"password":self.password})
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
    
    def CreateUser(self,username,password,first_name,last_name,email):
        data={'username':username,'password':password,'first_name':first_name,
              'last_name':last_name,'email':email}
        r=requests.post('https://api.software.dessia.tech/user/create',json=data)
        return r
    
    def VerifyEmail(self,token):
        data={'token':token}
        r=requests.post('https://api.software.dessia.tech/user/verify_email',json=data)
        return r
        
    def MyAccount(self):
        r=requests.get('https://api.software.dessia.tech/account/infos',headers=self.auth_header)
        return r
    
    def TransactionDetails(self,transaction_id):
        r=requests.get('https://api.software.dessia.tech/transaction/{}'.format(transaction_id),
                       headers=self.auth_header)
        return r
    
    def CreateTransaction(self,debitor_id,creditor_id,amount,debited,infos):
        data={'debitor_id':debitor_id,'creditor_id':creditor_id,'amount':amount,'debited':debited,'infos':infos}
        r=requests.post('https://api.software.dessia.tech/transaction/create',
                       headers=self.auth_header,json=data)
        return r
    
    def Model3DResultsKeys(self):
        r=requests.get('https://api.software.dessia.tech/powertransmission/database/model3d_results/keys',
                       headers=self.auth_header)
        return r
        
    def AddModel3DResult(self,result,name,infos,owner_type='user',owner_id=None):
        data={'result':jsonpickle.encode(result,keys=True),'name':name,'infos':infos}
        if owner_id:
            data['owner_type']=owner_type
            data['owner_id']=owner_id
        r=requests.post('https://api.software.dessia.tech/powertransmission/database/model3d_result/add',
                        headers=self.auth_header,json=data)
        return r
    
    def AddResult(self,result,name,infos,owner_type='user',owner_id=None):
        data={'result':jsonpickle.encode(result,keys=True),'name':name,'infos':infos}
        if owner_id:
            data['owner_type']=owner_type
            data['owner_id']=owner_id
        r=requests.post('https://api.software.dessia.tech/results/add',
                        headers=self.auth_header,json=data)
        return r
    
    def GetModel3DResult(self,id_result):
        r=requests.get('https://api.software.dessia.tech/powertransmission/database/model3d_result/{}/object'.format(id_result),
                       headers=self.auth_header)
        if r.status_code==200:
            return jsonpickle.decode(r.text,keys=True)
        else:
            return r
    
    def GetModel3DTextReport(self,id_result):
        r=requests.get('https://api.software.dessia.tech/powertransmission/database/model3d_result/{}/text_report'.format(id_result),
                       headers=self.auth_header)
        return r
        
    def SubmitModel3DOptimization(self,model3d,bounds_sl):
        data={'model3d_optimizer':jsonpickle.encode(model3d,keys=True),
              'bounds_shaft_lines':jsonpickle.encode(bounds_sl,keys=True),
              'infos':''}
        r=requests.post('https://api.software.dessia.tech/powertransmission/jobs/optimization3d/submit',
                        headers=self.auth_header,json=data)
        return r
    
    def SubmitJob(self,job_type,input_data):
        data={'job_type':job_type,'input_data':input_data}
        r=requests.post('https://api.software.dessia.tech/job/submit',
                        headers=self.auth_header,json=data)
        return r
        
    def JobDetails(self,job_id):
        r=requests.get('https://api.software.dessia.tech/job/{}/infos'.format(job_id),
                       headers=self.auth_header)
        return r


    def CompanyDetails(self,company_id):
        r=requests.get('https://api.software.dessia.tech/company/{}'.format(company_id),
                       headers=self.auth_header)
        return r
    
    def UserTeams(self):
        r=requests.get('https://api.software.dessia.tech/teams/list',
                       headers=self.auth_header)
        return r
    
    def CreateTeam(self,name,membership=True):
        data={'name':name,'membership':membership}
        r=requests.post('https://api.software.dessia.tech/team/create',
                       headers=self.auth_header,json=data)
        return r
    
    def CreateProject(self,name,owner_type='user',owner_id=None):
        data={'name':name,'owner_type':owner_type,'owner_id':owner_id}
        r=requests.post('https://api.software.dessia.tech/projects/create',
                       headers=self.auth_header,json=data)
        return r
    
    def Users(self,users_id):
        r=requests.post('https://api.software.dessia.tech/users',
                       headers=self.auth_header,json=users_id)
        return r
    
    def Teams(self,teams_id):
        r=requests.post('https://api.software.dessia.tech/teams',
                       headers=self.auth_header,json=teams_id)
        return r
    
    def MyTeamsInvitation(self):
        r=requests.get('https://api.software.dessia.tech/account/team_invitations',
                       headers=self.auth_header)
        return r
    