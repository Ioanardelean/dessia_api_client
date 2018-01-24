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
import getpass

import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
jsonpickle_numpy.register_handlers()


class AuthenticationError(Exception):
    pass
    
class Client:
    def __init__(self,email=None,password=None,token=None,api_url='https://api.software.dessia.tech'):

        self.email=email
        self.password=password
        self.token=token
        if self.token:
            self.token_exp=jwt.decode(self.token,verify=False)['exp']
        else:
            self.token_exp=0.
        self.api_url=api_url
#        self.token_nbf=time.time()
    def _get_auth_header(self):
        if self.token_exp<time.time():
            if (not self.email)|(not self.password):
                if self.email is None:
                    self.email=input('Email for DessIA API:')
                else:
                    print('Using {} as email'.format(self.email))
                if self.password is None:
                    self.password=getpass.getpass('Password for DessIA API:')
            print('Token expired, reauth')
            # Authenticate
            r = requests.post('{}/auth'.format(self.api_url), json={"email": self.email,"password":self.password})
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
        r=requests.post('{}/user/create'.format(self.api_url),json=data)
        return r
    
    def VerifyEmail(self,token):
        data={'token':token}
        r=requests.post('{}/user/verify_email'.format(self.api_url),json=data)
        return r
        
    def MyAccount(self):
        r=requests.get('{}/account/infos'.format(self.api_url),headers=self.auth_header)
        return r
    
    def TransactionDetails(self,transaction_id):
        r=requests.get('{}/transaction/{}'.format(transaction_id),
                       headers=self.auth_header)
        return r
    
    def CreateTransaction(self,debitor_id,creditor_id,amount,debited,infos):
        data={'debitor_id':debitor_id,'creditor_id':creditor_id,'amount':amount,'debited':debited,'infos':infos}
        r=requests.post('{}/transaction/create'.format(self.api_url),
                       headers=self.auth_header,json=data)
        return r
    
    def Model3DResultsKeys(self):
        r=requests.get('{}/powertransmission/database/model3d_results/keys'.format(self.api_url),
                       headers=self.auth_header)
        return r
        
    def AddModel3DResult(self,result,name,infos,owner_type='user',owner_id=None):
        data={'result':jsonpickle.encode(result,keys=True),'name':name,'infos':infos}
        if owner_id:
            data['owner_type']=owner_type
            data['owner_id']=owner_id
        r=requests.post('{}/powertransmission/database/model3d_result/add'.format(self.api_url),
                        headers=self.auth_header,json=data)
        return r
    
    def AddResult(self,result,name,infos,owner_type='user',owner_id=None):
        data={'result':jsonpickle.encode(result,keys=True),'name':name,'infos':infos}
        if owner_id:
            data['owner_type']=owner_type
            data['owner_id']=owner_id
        r=requests.post('{}/results/add'.format(self.api_url),
                        headers=self.auth_header,json=data)
        return r
    
    def GetModel3DResult(self,id_result):
        r=requests.get('{}/powertransmission/database/model3d_result/{}/object'.format(self.api_url,id_result),
                       headers=self.auth_header)
        if r.status_code==200:
            return jsonpickle.decode(r.text,keys=True)
        else:
            return r
    
    def GetModel3DTextReport(self,id_result):
        r=requests.get('{}/powertransmission/database/model3d_result/{}/text_report'.format(self.api_url,id_result),
                       headers=self.auth_header)
        return r
        
    def SubmitModel3DOptimization(self,model3d,bounds_sl):
        data={'model3d_optimizer':jsonpickle.encode(model3d,keys=True),
              'bounds_shaft_lines':jsonpickle.encode(bounds_sl,keys=True),
              'infos':''}
        r=requests.post('{}/powertransmission/jobs/optimization3d/submit'.format(self.api_url),
                        headers=self.auth_header,json=data)
        return r
    
    def SubmitJob(self,job_type,input_data):
        data={'job_type':job_type,'input_data':input_data}
        r=requests.post('{}/job/submit'.format(self.api_url),
                        headers=self.auth_header,json=data)
        return r
        
    def JobDetails(self,job_id):
        r=requests.get('{}/job/{}/infos'.format(self.api_url,job_id),
                       headers=self.auth_header)
        return r


    def CompanyDetails(self,company_id):
        r=requests.get('{}/company/{}'.format(self.api_url,company_id),
                       headers=self.auth_header)
        return r
    
    def UserTeams(self):
        r=requests.get('{}/teams/list'.format(self.api_url),
                       headers=self.auth_header)
        return r
    
    def CreateTeam(self,name,membership=True):
        data={'name':name,'membership':membership}
        r=requests.post('{}/team/create'.format(self.api_url),
                       headers=self.auth_header,json=data)
        return r
    
    def CreateProject(self,name,owner_type='user',owner_id=None):
        data={'name':name,'owner_type':owner_type,'owner_id':owner_id}
        r=requests.post('{}/projects/create'.format(self.api_url),
                       headers=self.auth_header,json=data)
        return r
    
    def Users(self,users_id):
        r=requests.post('{}/users'.format(self.api_url),
                       headers=self.auth_header,json=users_id)
        return r
    
    def Teams(self,teams_id):
        r=requests.post('{}/teams'.format(self.api_url),
                       headers=self.auth_header,json=teams_id)
        return r
    
    def MyTeamsInvitation(self):
        r=requests.get('{}/account/team_invitations'.format(self.api_url),
                       headers=self.auth_header)
        return r
    