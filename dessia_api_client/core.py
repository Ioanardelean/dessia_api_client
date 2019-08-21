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

class APIConnectionError(Exception):
    pass


def retry_n_times(func):
   def func_wrapper(self, *args, **kwargs):
       connection_error = True
       n_tries = 1
       while connection_error and (n_tries < self.max_retries):
           try:
               r = func(self, *args, **kwargs)            
#               if str(r.status_code)[0] == '2':
               connection_error = False
               break
           except requests.ConnectionError: 
               connection_error = True
           
           print('Connection with api down, retry {}/{} in {} seconds'.format(n_tries,
                                                                              self.max_retries,
                                                                              self.retry_interval))
           n_tries += 1
           time.sleep(self.retry_interval)
       if connection_error:
           raise APIConnectionError
       else:
           return r
   return func_wrapper

class Filter:
    def __init__(self, attribute, operator, value):
        self.attribute = attribute
        self.operator = operator
        self.value = value
        
    def to_param(self):
        return {'{}[{}]'.format(self.attribute, self.operator): self.value}
        
class EqualityFilter(Filter):
    def __init__(self, attribute, value):
        Filter.__init__(self, attribute, 'eq', value)

class LowerFilter(Filter):
    def __init__(self, attribute, value):
        Filter.__init__(self, attribute, 'lt', value)
        
class LowerOrEqualFilter(Filter):
    def __init__(self, attribute, value):
        Filter.__init__(self, attribute, 'lte', value)

class GreaterFilter(Filter):
    def __init__(self, attribute, value):
        Filter.__init__(self, attribute, 'gt', value)
        
class GreaterOrEqualFilter(Filter):
    def __init__(self, attribute, value):
        Filter.__init__(self, attribute, 'gte', value)



class Client:
    def __init__(self,
                 username=None,
                 password=None,
                 token=None,
                 proxies=None,
                 api_url='https://api.software.dessia.tech',
                 max_retries=10,
                 retry_interval=2):

        self.username = username
        self.password = password
        self.token = token
        self.proxies = proxies
        if self.token:
            self.token_exp = jwt.decode(self.token, verify=False)['exp']
        else:
            self.token_exp = 0.
        self.api_url = api_url
        self.max_retries = max_retries
        self.retry_interval = retry_interval

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
                                    "password":self.password},
                              proxies=self.proxies)
            if r.status_code == 200:
                self.token = r.json()['access_token']
                self.token_exp = jwt.decode(self.token, verify=False)['exp']
                print('Auth in {}s'.format(r.elapsed.total_seconds()))
            else:
                print(r.text)
                raise AuthenticationError

        auth_header = {'Authorization':'Bearer {}'.format(self.token)}
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

        r = requests.post('{}/users/create'.format(self.api_url),
                          json=data,
                          proxies=self.proxies)

        return r

    def CreateTechnicalAccount(self, name, password):
        data = {'name': name,
                'password': password}

        r = requests.post('{}/technical_accounts/create'.format(self.api_url),
                          json=data,
                          headers=self.auth_header,
                          proxies=self.proxies)

        return r

    def VerifyEmail(self, token):
        data = {'token':token}
        r = requests.post('{}/account/verify-email'.format(self.api_url),
                          json=data,
                          proxies=self.proxies)
        return r

    @retry_n_times
    def request_my_account(self):
        r = requests.get('{}/account/infos'.format(self.api_url),
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r


    def SubmitJob(self, obj, id_, method, arguments={}):
        data = {'object': {'class': '{}.{}'.format(obj.__class__.__module__, obj.__class__.__name__),
                           'id': id_},
                'method': method,
                'arguments': arguments
                }
        r = requests.post('{}/jobs/submit'.format(self.api_url),
                          headers=self.auth_header,
                          json=data,
                          proxies=self.proxies)
        return r

    def JobDetails(self, job_id):
        r = requests.get('{}/jobs/{}'.format(self.api_url, job_id),
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r


    def CompanyDetails(self, company_id):
        r = requests.get('{}/companies/{}'.format(self.api_url, company_id),
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r

    def UserTeams(self):
        r = requests.get('{}/teams/list'.format(self.api_url),
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r

    def CreateTeam(self, name, membership=True):
        data = {'name':name,
                'membership':membership}
        r = requests.post('{}/teams'.format(self.api_url),
                          headers=self.auth_header,
                          json=data,
                          proxies=self.proxies)
        return r

    def CreateProject(self, name, owner_type='user', owner_id=None):
        data = {'name':name,
                'owner_type': owner_type,
                'owner_id': owner_id}
        r = requests.post('{}/projects'.format(self.api_url),
                          headers=self.auth_header,
                          json=data,
                          proxies=self.proxies)
        return r

    def CreateJob(self, celery_id, owner_type, owner_id):
        data = {'celery_id': celery_id,
                'owner_type': owner_type,
                'owner_id': owner_id}
        r = requests.post('{}/jobs/create'.format(self.api_url),
                          headers=self.auth_header,
                          json=data,
                          proxies=self.proxies)
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
                          headers=self.auth_header,
                          json=users_id,
                          proxies=self.proxies)
        return r

    def Teams(self, teams_id):
        r = requests.post('{}/teams'.format(self.api_url),
                          headers=self.auth_header,
                          json=teams_id,
                          proxies=self.proxies)
        return r

    def MyTeamsInvitation(self):
        r = requests.get('{}/account/team_invitations'.format(self.api_url),
                         headers=self.auth_header,
                          proxies=self.proxies)
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
                        headers=self.auth_header,
                        json=data,
                        proxies=self.proxies)

        return r

    def GetObjectClasses(self):
        r = requests.get('{}/objects/classes'.format(self.api_url),
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r

    def GetClassHierarchy(self):
        r = requests.get('{}/objects/class_hierarchy'.format(self.api_url),
                         headers=self.auth_header,
                         proxies=self.proxies)
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
                         headers=self.auth_header,
                         proxies=self.proxies)
        return request

    def GetObject(self, object_class, object_id, instantiate=True):
        payload = {'embedded_subobjects': str(instantiate).casefold()}
        r = requests.get('{}/objects/{}/{}'.format(self.api_url,
                                                   object_class,
                                                   object_id),
                         headers=self.auth_header,
                         params=payload,
                         proxies=self.proxies)
        if instantiate:
            module_name = '.'.join(object_class.split('.')[:-1])
            class_name = object_class.split('.')[-1]
            module = importlib.import_module(module_name)
            object_class = getattr(module, class_name)
            return object_class.DictToObject(r.json()['object_dict'])
        return r

    def GetObjectPlotData(self, object_class, object_id):
        r = requests.get('{}/objects/{}/{}/plot_data'.format(self.api_url, object_class, object_id),
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r

    def GetObjectSTLToken(self, object_class, object_id):
        r = requests.get('{}/objects/{}/{}/stl'.format(self.api_url, object_class, object_id),
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r

    def GetAllClassObjects(self, object_class):
        r = requests.get('{}/objects/{}'.format(self.api_url, object_class),
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r


    def CreateObject(self, obj, owner=None, embedded_subobjects=True, public=False):
        data = {'object': {'class': '{}.{}'.format(obj.__class__.__module__, obj.__class__.__name__),
                           'json': StringifyDictKeys(obj.Dict())},
                'embedded_subobjects': embedded_subobjects,
                'public': public}
#        print(data)
        if owner is not None:
            data['owner'] = owner
        r = requests.post('{}/objects/create'.format(self.api_url),
                          headers=self.auth_header,
                          json=data,
                          proxies=self.proxies)
        return r

    @retry_n_times
    def ReplaceObject(self, object_class, object_id, new_object,
                      embedded_subobjects = False, owner=None):
        data = {'object': {'class': object_class,
                           'json': StringifyDictKeys(new_object.Dict())},
                'embedded_subobjects' : embedded_subobjects}
        if owner is not None:
            data['owner'] = owner
        r = requests.post('{}/objects/{}/{}/replace'.format(self.api_url, object_class, object_id),
                        headers=self.auth_header,
                        json=data,
                        proxies=self.proxies)
        return r

    def UpdateObject(self, object_class, object_id, update_dict):
        r = requests.post('{}/objects/{}/{}/update'.format(self.api_url, object_class, object_id),
                        headers=self.auth_header,
                        json=update_dict,
                        proxies=self.proxies)
        return r

    def delete_object(self, object_class, object_id):
        r = requests.delete('{}/objects/{}/{}/delete'.format(self.api_url, object_class, object_id),
                            headers=self.auth_header,
                            proxies=self.proxies)
        return r

    def DeleteAllSTL(self):
        r = requests.delete('{}/objects/stl/delete_all'.format(self.api_url),
                        headers=self.auth_header,
                        proxies=self.proxies)
        return r
    
    @retry_n_times
    def request_marketplace_stats(self):
        r = requests.get('{}/marketplace/stats'.format(self.api_url),
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r
    
    @retry_n_times
    def request_get_manufacturers(self, limit, offset):
        parameters = {'limit': limit, 'offset': offset}
        r = requests.get('{}/marketplace/manufacturers'.format(self.api_url),
                         params=parameters,
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r  
    
    def get_all_manufacturers(self):
        return self._get_all_elements('get_manufacturers')
    
    def get_manufacturers(self, limit=20, offset=0):
        r = self.request_get_manufacturers(limit, offset)
        return r.json()



    def request_create_manufacturer(self, name, url, country):
        data = {'name': name,
                'url': url,
                'country': country}
        r = requests.post('{}/marketplace/manufacturers'.format(self.api_url),
                          headers=self.auth_header, json=data,
                          proxies=self.proxies)
        return r

    
    @retry_n_times
    def request_get_brands(self, limit, offset):
        parameters = {'limit': limit, 'offset': offset}
        r = requests.get('{}/marketplace/brands'.format(self.api_url),
                         params=parameters,
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r  
    
    def get_all_brands(self):
        return self._get_all_elements('get_brands')
    
    def get_brands(self, limit=20, offset=0):
        r = self.request_get_brands(limit, offset)
        return r.json()
    
    def create_brand(self, name, url, country, manufacturer_id):
        data = {'name': name,
                'url': url,
                'country': country,
                'manufacturer_id': manufacturer_id}
        r = requests.post('{}/marketplace/brands'.format(self.api_url),
                          headers=self.auth_header,
                          json=data,
                          proxies=self.proxies)
        return r
    
    def create_product(self, name, url, brand_id, object_class, object_id,
                       image_url=None, documentation_url=None):
        data = {'name': name,
                'url': url,
                'brand_id': brand_id,
                'object_class': object_class,
                'object_id': object_id}
        
        if image_url is not None:
            data['image_url'] = image_url
        if documentation_url is not None:
            data['documentation_url'] = documentation_url
        
        r = requests.post('{}/marketplace/products'.format(self.api_url),
                          headers=self.auth_header,
                          json=data,
                          proxies=self.proxies)
        return r
    
    
    def _get_all_elements(self, method_name, query_size=500):
        elements = []
        offset = 0        
        query_empty = False
        while not query_empty:            
            query_list = getattr(self, method_name)(limit=query_size,
                                                    offset=offset)['filtered_results']
            query_empty = len(query_list) == 0
            elements.extend(query_list)
            offset += query_size
        return elements
    
    @retry_n_times
    def request_get_products(self, limit, offset, filters=[], order=None):
        parameters = {'limit': limit,
                      'offset': offset,
                   }
        for f in filters:
            parameters.update(f.to_param())
            
        if order is not None:
            parameters['order'] = order
        
        r = requests.get('{}/marketplace/products'.format(self.api_url),
                         params=parameters,
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r  
    
    
    def get_all_products(self):
        return self._get_all_elements('get_products')
    
    def get_products(self, limit=100, offset=0, filters=[]):
        r = self.request_get_products(limit, offset, filters)
        return r.json()
    
    @retry_n_times
    def request_get_product(self, product_id):
        r = requests.get('{}/marketplace/products/{}'.format(self.api_url,
                                                             product_id),
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r
        
    @retry_n_times
    def request_get_retailers(self, limit, offset):
        parameters = {'limit': limit, 'offset': offset}
        r = requests.get('{}/marketplace/retailers'.format(self.api_url),
                         params=parameters,
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r  
    
    def get_all_retailers(self):
        return self._get_all_elements('get_retailers')
    
    def get_retailers(self, limit=20, offset=0):
        r = self.request_get_retailers(limit, offset)
        return r.json()
    
    
    def request_create_retailer(self, name, url, country):
        data = {'name': name,
                'url': url,
                'country': country}
        r = requests.post('{}/marketplace/retailers'.format(self.api_url),
                          headers=self.auth_header,
                          json=data,
                          proxies=self.proxies)
        return r
    
    @retry_n_times
    def request_get_skus(self, limit, offset, filters=[]):
        parameters = {'limit': limit, 'offset': offset}
        for f in filters:
            parameters.update(f.to_param())
            
        r = requests.get('{}/marketplace/stock-keeping-units'.format(self.api_url),
                         params=parameters,
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r 
    
    def get_all_skus(self):
        return self._get_all_elements('get_skus')
    
    def get_skus(self, limit=20, offset=0, filters=[]):
        r = self.request_get_skus(limit, offset, filters)
#        print(r.text)
        return r.json()

    def request_update_sku_price_offers(self, sku_id, new_price_offers):
        r = requests.put('{}/marketplace/stock-keeping-units/{}/price-offers'.format(self.api_url, sku_id),
                         headers=self.auth_header,
                         json=new_price_offers,
                         proxies=self.proxies)
        return r
    
    
    def request_create_sku(self, product_id, number_products, url, retailer_id):
        data = {'product_id': product_id,
                'number_products': number_products,
                'url': url,
                'retailer_id': retailer_id}
        r = requests.post('{}/marketplace/stock-keeping-units'.format(self.api_url),
                          headers=self.auth_header,
                          json=data,
                          proxies=self.proxies)
        return r
    
    @retry_n_times
    def request_get_price_offers(self, limit, offset):
        parameters = {'limit': limit, 'offset': offset}
        r = requests.get('{}/marketplace/price-offers'.format(self.api_url),
                         params=parameters,
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r  
    
    def get_all_price_offers(self):
        return self._get_all_elements('get_price_offers')
    
    def get_price_offers(self, limit=20, offset=0):
        r = self.request_get_price_offers(limit, offset)
        return r.json()

    
    def request_create_price_offer(self, sku_id, unit_price, currency, min_quantity, max_quantity=None):
        data = {'sku_id': sku_id,
                'min_quantity': min_quantity,
                'unit_price': unit_price,
                'currency': currency}
        if max_quantity is not None:
            data['max_quantity'] = max_quantity
            
        r = requests.post('{}/marketplace/price-offers'.format(self.api_url),
                          headers=self.auth_header,
                          json=data,
                          proxies=self.proxies)
        return r