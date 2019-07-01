#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 10:35:32 2017

@author: steven
"""



import jwt
import time
import getpass
import importlib
import requests

def StringifyDictKeys(d):
    if type(d) == list or type(d) == tuple:
        new_d = []
        for di in d:
            new_d.append(StringifyDictKeys(di))

    elif type(d) == dict:
        new_d = {}
        for k, v in d.items():
            new_d[str(k)] = StringifyDictKeys(v)
    else:
        return d
    return new_d

class AuthenticationError(Exception):
    pass

class Client:
    def __init__(self,
                 username=None,
                 password=None,
                 token=None,
                 api_url='https://api.software.dessia.tech'):

        self.username = username
        self.password = password
        self.token = token
        if self.token:
            self.token_exp = jwt.decode(self.token, verify=False)['exp']
        else:
            self.token_exp = 0.
        self.api_url = api_url


    def _get_auth_header(self):
        if self.token_exp < time.time():
            if (not self.username)|(not self.password):
                if self.username is None:
                    self.username = input('Email(User)/name(Technical Account) for DessIA API:')
                else:
                    print('Using {} as email'.format(self.username))
                if self.password is None:
                    self.password = getpass.getpass('Password for DessIA API:')
            print('Token expired, reauth')
            # Authenticate
            r = requests.post('{}/auth'.format(self.api_url),
                              json={"username": self.username,
                                    "password":self.password})
            if r.status_code == 200:
                self.token = r.json()['access_token']
                self.token_exp = jwt.decode(self.token, verify=False)['exp']
                print('Auth in {}s'.format(r.elapsed.total_seconds()))
            else:
                print(r.text)
                raise AuthenticationError

        auth_header = {'Authorization':'JWT {}'.format(self.token)}
        return auth_header

    auth_header = property(_get_auth_header)

    def CreateUser(self, email, password, first_name, last_name, standalone_user=True):
        data = {'email':email,
                'password':password,
                'first_name':first_name,
                'last_name':last_name}

        if standalone_user:
            data['user_type'] = 'StandAloneUser'
        else:
            data['user_type'] = 'OrganizationUser'

        r = requests.post('{}/users/create'.format(self.api_url), json=data)

        return r

    def CreateTechnicalAccount(self, name, password):
        data = {'name': name,
                'password': password}

        r = requests.post('{}/technical_accounts/create'.format(self.api_url),
                          json=data,
                          headers=self.auth_header)

        return r

    def VerifyEmail(self, token):
        data = {'token':token}
        r = requests.post('{}/account/verify-email'.format(self.api_url),
                          json=data)
        return r

    def MyAccount(self):
        r = requests.get('{}/account/infos'.format(self.api_url),
                         headers=self.auth_header)
        return r


    def SubmitJob(self, job_type, input_data):
        data = {'analysis_type': job_type,
                'input_data': input_data}
        r = requests.post('{}/jobs/submit'.format(self.api_url),
                          headers=self.auth_header, json=data)
        return r

    def JobDetails(self, job_id):
        r = requests.get('{}/job/{}/infos'.format(self.api_url, job_id),
                         headers=self.auth_header)
        return r


    def CompanyDetails(self, company_id):
        r = requests.get('{}/companies/{}'.format(self.api_url, company_id),
                         headers=self.auth_header)
        return r

    def UserTeams(self):
        r = requests.get('{}/teams/list'.format(self.api_url),
                         headers=self.auth_header)
        return r

    def CreateTeam(self, name, membership=True):
        data = {'name':name,
                'membership':membership}
        r = requests.post('{}/teams/create'.format(self.api_url),
                          headers=self.auth_header, json=data)
        return r

    def CreateProject(self, name, owner_type='user', owner_id=None):
        data = {'name':name,
                'owner_type': owner_type,
                'owner_id': owner_id}
        r = requests.post('{}/projects/create'.format(self.api_url),
                          headers=self.auth_header, json=data)
        return r

    def CreateJob(self, celery_id, owner_type, owner_id):
        data = {'celery_id': celery_id,
                'owner_type': owner_type,
                'owner_id': owner_id}
        r = requests.post('{}/jobs/create'.format(self.api_url),
                          headers=self.auth_header, json=data)
        return r

#    def SubmitJob(self,job_type,input_data,owner_type='user',owner_id=None):
#        data={'job_type':job_type,'input_data':input_data}
#        if owner_id:
#            data['owner_type']=owner_type
#            data['owner_id']=owner_id
#        r=requests.post('https://api.software.dessia.tech/jobs/submit',
#                        headers=self.auth_header,json=data)
#        return r


    def Users(self, users_id):
        r = requests.post('{}/users'.format(self.api_url),
                          headers=self.auth_header, json=users_id)
        return r

    def Teams(self, teams_id):
        r = requests.post('{}/teams'.format(self.api_url),
                          headers=self.auth_header, json=teams_id)
        return r

    def MyTeamsInvitation(self):
        r = requests.get('{}/account/team_invitations'.format(self.api_url),
                         headers=self.auth_header)
        return r


    def CreateUserCreditOperation(self,
                                  number_hours,
                                  user_id=None,
                                  validated=None,
                                  price=None,
                                  caption=''):
        data = {'number_hours':number_hours,
                'caption':caption}
        if user_id is not None:
            data['user_id'] = user_id
        if validated is not None:
            data['validated'] = validated
        if price is not None:
            data['price'] = price
        r = requests.post('{}/quotes/user_credit/create'.format(self.api_url),
                        headers=self.auth_header, json=data)

        return r

    def GetObjectClasses(self):
        r = requests.get('{}/objects/classes'.format(self.api_url),
                         headers=self.auth_header)
        return r

    def GetClassHierarchy(self):
        r = requests.get('{}/objects/class_hierarchy'.format(self.api_url),
                         headers=self.auth_header)
        return r

#    def GetClassComposition(self, class_):
#        r = requests.get('{}/objects/class_composition/{}'.format(self.api_url, class_),
#                        headers=self.auth_header)
#        return r

    def get_class_attributes(self, class_):
        """
        Gets class attributes (_standalone_in_db, _jsonschema, and other class data)
        """
        request = requests.get('{}/objects/{}/attributes'.format(self.api_url, class_),
                         headers=self.auth_header)
        return request

    def GetObject(self, object_class, object_id, instantiate=True):
        payload = {'embedded_subobjects': str(instantiate).casefold()}
        r = requests.get('{}/objects/{}/{}'.format(self.api_url,
                                                   object_class,
                                                   object_id),
                         headers=self.auth_header,
                         params=payload)
        if instantiate:
            module_name = '.'.join(object_class.split('.')[:-1])
            class_name = object_class.split('.')[-1]
            module = importlib.import_module(module_name)
            object_class = getattr(module, class_name)
            return object_class.DictToObject(r.json()['object_dict'])
        return r

    def GetObjectPlotData(self, object_class, object_id):
        r = requests.get('{}/objects/{}/{}/plot_data'.format(self.api_url, object_class, object_id),
                         headers=self.auth_header)
        return r

    def GetObjectSTLToken(self, object_class, object_id):
        r = requests.get('{}/objects/{}/{}/stl'.format(self.api_url, object_class, object_id),
                         headers=self.auth_header)
        return r

    def GetAllClassObjects(self, object_class):
        r = requests.get('{}/objects/{}'.format(self.api_url, object_class),
                         headers=self.auth_header)
        return r


    def CreateObject(self, obj, owner=None):
        data = {'object': {'class': '{}.{}'.format(obj.__class__.__module__, obj.__class__.__name__),
                           'json': StringifyDictKeys(obj.Dict())}}
        if owner is not None:
            data['owner'] = owner
        r = requests.post('{}/objects/create'.format(self.api_url),
                          headers=self.auth_header, json=data)
        return r


    def ReplaceObject(self, object_class, object_id, new_object,
                      embedded_subobjects = False, owner=None):
        data = {'object': {'class': object_class,
                           'json': StringifyDictKeys(new_object.Dict())},
                'embedded_subobjects' : embedded_subobjects}
        if owner is not None:
            data['owner'] = owner
        r = requests.post('{}/objects/{}/{}/replace'.format(self.api_url, object_class, object_id),
                        headers=self.auth_header, json=data)
        return r

    def UpdateObject(self, object_class, object_id, update_dict):
        r = requests.post('{}/objects/{}/{}/update'.format(self.api_url, object_class, object_id),
                        headers=self.auth_header, json=update_dict)
        return r

    def delete_object(self, object_class, object_id):
        r = requests.delete('{}/objects/{}/{}/delete'.format(self.api_url, object_class, object_id),
                            headers=self.auth_header)
        return r

    def DeleteAllSTL(self):
        r = requests.delete('{}/objects/stl/delete_all'.format(self.api_url),
                        headers=self.auth_header)
        return r