#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


"""

import jwt
import time
import getpass
import importlib
import requests
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
try:
    import dessia_common as dc
except ModuleNotFoundError:
    msg = 'Dessia common module could not be found.\n'
    msg += 'It is required for object handling.'
    print()
import string
import random


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
            log = 'Connection with api down, retry {}/{} in {} seconds'
            print(log.format(n_tries, self.max_retries, self.retry_interval))
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


class InFilter(Filter):
    def __init__(self, attribute, values):
        Filter.__init__(self, attribute, 'in', values)


def instantiate_object(json):
    module_name, class_name = json['object_class'].rsplit('.', 1)
    module = importlib.import_module(module_name)
    object_class = getattr(module, class_name)
    return object_class.dict_to_object(json['object_dict'])


def confirm(action: str = 'Action'):
    validator = ''.join(random.choices(string.ascii_uppercase, k=6))
    print('Confirm by typing in following code : {}'.format(validator))
    print('Let empty to abort.\n')
    validation = input()
    if validation == validator:
        return True
    elif not validation:
        print('\n{} aborted'.format(action))
        return False
    else:
        print('\nInput did not match validator. {} aborted'.format(action))
        return False


class Client:
    def __init__(self, username=None, password=None, token=None,
                 proxies=None, api_url='https://api.platform.dessia.tech',
                 max_retries=10, retry_interval=2):
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

    def generate_token(self):
        if self.token_exp < time.time():
            if (not self.username) | (not self.password):
                if self.username is None:
                    log = 'Email(User)/name(Technical Account) for DessIA API:'
                    self.username = input(log)
                else:
                    print('Using {} as email'.format(self.username))
                if self.password is None:
                    self.password = getpass.getpass('Password for DessIA API:')
            print('No valid token stored, authentication...')
            # Authenticate
            r = requests.post('{}/auth'.format(self.api_url),
                              json={"username": self.username,
                                    "password": self.password},
                              proxies=self.proxies)
            if r.status_code == 200:
                self.token = r.json()['access_token']
                self.token_exp = jwt.decode(self.token, verify=False)['exp']
                print('Auth in {}s'.format(r.elapsed.total_seconds()))
            else:
                print('Authentication error: ', r.text)
                raise AuthenticationError

    @property
    def auth_header(self):
        self.generate_token()

        auth_header = {'Authorization': 'Bearer {}'.format(self.token)}
        return auth_header

    def create_user(self, email, password, first_name, last_name):
        data = {'email': email, 'password': password,
                'first_name': first_name, 'last_name': last_name}
        r = requests.post('{}/users'.format(self.api_url),
                          json=data, proxies=self.proxies)
        return r
    
    def send_verification_email(self, email):
        parameters = {'email': email}
        url = '{}/account/send-verification-code'
        r = requests.get(url.format(self.api_url),
                         params=parameters, proxies=self.proxies)

        return r

    def CreateTechnicalAccount(self, name, password):
        data = {'name': name,
                'password': password}
        url = '{}/technical_accounts/create'
        r = requests.post(url.format(self.api_url), json=data,
                          headers=self.auth_header, proxies=self.proxies)
        return r

    def verify_email(self, token):
        data = {'token': token}
        r = requests.post('{}/account/verify'.format(self.api_url),
                          json=data, proxies=self.proxies)
        return r

    @retry_n_times
    def request_my_account(self):
        r = requests.get('{}/account/infos'.format(self.api_url),
                         headers=self.auth_header, proxies=self.proxies)
        return r

    def SubmitJob(self, object_class, id_, method, arguments=None):
        if arguments is None:
            arguments = {}
        serialized_arguments = dc.serialize_dict(arguments)
        data = {'object': {'object_class': object_class, 'id': id_},
                'method': method, 'method_dict': serialized_arguments}
        r = requests.post('{}/jobs/submit'.format(self.api_url), json=data,
                          headers=self.auth_header, proxies=self.proxies)
        return r

    def JobDetails(self, job_id: int):
        r = requests.get('{}/jobs/{}'.format(self.api_url, job_id),
                         headers=self.auth_header, proxies=self.proxies)
        return r

    def get_organization(self, organization_id: int):
        url = '{}/organizations/{}'
        r = requests.get(url.format(self.api_url, organization_id),
                         headers=self.auth_header, proxies=self.proxies)
        return r
    
    def create_organization(self, name: str, type_: str):
        data = {'name': name, 'type': type_}
        r = requests.post('{}/organizations'.format(self.api_url), json=data,
                          headers=self.auth_header, proxies=self.proxies)
        return r

    def get_workspace(self, workspace_id: int):
        r = requests.get('{}/workspaces/{}'.format(self.api_url, workspace_id),
                         headers=self.auth_header, proxies=self.proxies)
        return r

    def create_workspace(self, name: str, organization_id: int):
        data = {'name': name}
        url = '{}/organizations/{}/workspaces'
        r = requests.post(url.format(self.api_url, organization_id), json=data,
                          headers=self.auth_header, proxies=self.proxies)
        return r

    def CreateJob(self, celery_id, owner_type, owner_id):
        data = {'celery_id': celery_id,
                'owner_type': owner_type,
                'owner_id': owner_id}
        r = requests.post('{}/jobs/create'.format(self.api_url), json=data,
                          headers=self.auth_header, proxies=self.proxies)
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

    def get_class_attributes(self, class_):
        """
        Gets class attributes
        (_standalone_in_db, _jsonschema, and other class data)
        """
        url = '{}/objects/{}/attributes'
        request = requests.get(url.format(self.api_url, class_),
                               headers=self.auth_header, proxies=self.proxies)
        return request

    def GetObject(self, object_class: str, object_id: str,
                  instantiate: bool = True):
        payload = {'embedded_subobjects': str(instantiate).casefold()}
        url = '{}/objects/{}/{}'
        r = requests.get(url.format(self.api_url, object_class, object_id),
                         headers=self.auth_header, params=payload,
                         proxies=self.proxies)
        if instantiate and r.status_code == 200:
            return instantiate_object(r.json())
        return r

    def get_subobject(self, object_class: str, object_id: str,
                      deep_attribute: str = None, instantiate: bool = True):
        payload = {'embedded_subobjects': str(instantiate).casefold()}
        url = '{}/objects/{}/{}/{}'.format(self.api_url, object_class,
                                           object_id, deep_attribute)
        req = requests.get(url, headers=self.auth_header,
                           params=payload, proxies=self.proxies)
        if instantiate:
            result = req.json()
            if dc.is_sequence(result):
                return [instantiate_object(v) for v in result]
            else:
                return instantiate_object(result)
        return req

    def GetObjectPlotData(self, object_class, object_id):
        url = '{}/objects/{}/{}/plot-data'
        r = requests.get(url.format(self.api_url, object_class, object_id),
                         headers=self.auth_header, proxies=self.proxies)
        return r

    def GetObjectSTLToken(self, object_class, object_id):
        url = '{}/objects/{}/{}/stl'
        r = requests.get(url.format(self.api_url, object_class, object_id),
                         headers=self.auth_header, proxies=self.proxies)
        return r

    def GetAllClassObjects(self, object_class):
        r = requests.get('{}/objects/{}'.format(self.api_url, object_class),
                         headers=self.auth_header, proxies=self.proxies)
        return r

    def object_display(self, object_class, object_id):
        url = '{}/objects/{}/{}/object_display'
        r = requests.get(url.format(self.api_url, object_class, object_id),
                         headers=self.auth_header, proxies=self.proxies)
        return r

    @retry_n_times
    def create_object_from_python_object(self, obj, owner=None,
                                         embedded_subobjects=True,
                                         public=False):
        
        data = {
            'object': {
                'object_class': '{}.{}'.format(obj.__class__.__module__,
                                               obj.__class__.__name__),
                'json': StringifyDictKeys(obj.to_dict())
            },
            'embedded_subobjects': embedded_subobjects,
            'public': public}
        if owner is not None:
            data['owner'] = owner
        r = requests.post('{}/objects'.format(self.api_url), json=data,
                          headers=self.auth_header, proxies=self.proxies)
        return r

    @retry_n_times
    def create_object_from_object_dict(self, object_dict, owner=None,
                                       embedded_subobjects=True, public=False):
        data = {'object': {'object_class': object_dict['object_class'],
                           'json': StringifyDictKeys(object_dict)},
                'embedded_subobjects': embedded_subobjects,
                'public': public}
        if owner is not None:
            data['owner'] = owner
        r = requests.post('{}/objects'.format(self.api_url),
                          headers=self.auth_header,
                          json=data,
                          proxies=self.proxies)
        return r

    @retry_n_times
    def ReplaceObject(self, object_class, object_id, new_object,
                      embedded_subobjects: bool = False, owner=None):
        data = {'object': {'object_class': object_class,
                           'json': StringifyDictKeys(new_object.to_dict())},
                'embedded_subobjects': embedded_subobjects}
        if owner is not None:
            data['owner'] = owner
        url = '{}/objects/{}/{}/replace'
        r = requests.post(url.format(self.api_url, object_class, object_id),
                          headers=self.auth_header, json=data,
                          proxies=self.proxies)
        print(r.status_code)
        return r

    def UpdateObject(self, object_class, object_id, update_dict):
        url = '{}/objects/{}/{}/update'
        r = requests.post(url.format(self.api_url, object_class, object_id),
                          headers=self.auth_header, json=update_dict,
                          proxies=self.proxies)
        return r

    def delete_object(self, object_class, object_id):
        url = '{}/objects/{}/{}'
        r = requests.delete(url.format(self.api_url, object_class, object_id),
                            headers=self.auth_header, proxies=self.proxies)
        return r

    def delete_all_objects_from_class(self, object_class=''):
        objects = self.GetAllClassObjects(object_class).json()
        log = '\nThis will delete {} objects from class {}'
        print(log.format(len(objects), object_class))
        confirmed = confirm('Deletion')
        if confirmed:
            url = '{}/objects/{}'
            r = requests.delete(url.format(self.api_url, object_class),
                                headers=self.auth_header, proxies=self.proxies)
            return r

    def delete_all_objects(self):
        print('\nThis will delete all objects from database.')
        confirmed = confirm('Deletion')
        if confirmed:
            url = '{}/objects'
            r = requests.delete(url.format(self.api_url),
                                headers=self.auth_header, proxies=self.proxies)
            return r
    
    def method_attributes(self, object_class, object_id):
        url = '{}/objects/{}/{}/method_attributes'
        r = requests.get(url.format(self.api_url, object_class, object_id),
                         headers=self.auth_header, proxies=self.proxies)
        return r
    
    @retry_n_times
    def request_marketplace_stats(self):
        r = requests.get('{}/marketplace/stats'.format(self.api_url),
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r
    
    def get_manufacturers(self, limit=20, offset=0, filters=None):
        if filters is None:
            filters = []
        r = self.request_get_elements('manufacturer', limit,
                                      offset, filters=filters)
        return r.json()

    def request_create_manufacturer(self, name, url, country):
        data = {'name': name, 'url': url, 'country': country}
        url = '{}/marketplace/manufacturers'
        r = requests.post(url.format(self.api_url), json=data,
                          headers=self.auth_header, proxies=self.proxies)
        return r
    
    def get_brands(self, limit=20, offset=0, filters=None):
        if filters is None:
            filters = []
        r = self.request_get_elements('brand', limit, offset, filters)
        return r.json()
    
    @retry_n_times
    def request_create_brand(self, name, url, country, manufacturer_id):
        data = {'name': name, 'url': url, 'country': country,
                'manufacturer_id': manufacturer_id}
        url = '{}/marketplace/brands'
        r = requests.post(url.format(self.api_url), json=data,
                          headers=self.auth_header, proxies=self.proxies)
        return r
    
    def create_product(self, name, url, brand_id, object_class, object_id,
                       image_urls=None, documentation_url=None):
        data = {'name': name, 'url': url, 'brand_id': brand_id,
                'object_class': object_class, 'object_id': object_id}
        
        if image_urls is not None:
            data['image_urls'] = image_urls
        else:
            data['image_urls'] = []
            
        if documentation_url is not None:
            data['documentation_url'] = documentation_url

        url = '{}/marketplace/products'
        r = requests.post(url.format(self.api_url), json=data,
                          headers=self.auth_header, proxies=self.proxies)
        return r
    
    def request_add_imageurl_to_product(self, product_id, image_url):
        url = '{}/marketplace/products/{}/image_urls'
        r = requests.post(url.format(self.api_url, product_id),
                          headers=self.auth_header, json={'url': image_url},
                          proxies=self.proxies)
        return r
    
    def get_all_elements(self, element_name, filters=None, query_size=500):
        elements = []
        offset = 0        
        query_empty = False
        while not query_empty:
            callable_ = getattr(self, 'get_{}s'.format(element_name))
            results = callable_(limit=query_size, offset=offset,
                                filters=filters)
            query_list = results['filtered_results']
            query_empty = len(query_list) == 0
            elements.extend(query_list)
            offset += query_size
        return elements
    
    @retry_n_times
    def request_get_element(self, element_name, element_id):
        url = '{}/marketplace/{}s/{}'
        r = requests.get(url.format(self.api_url, element_name, element_id),
                         headers=self.auth_header, proxies=self.proxies)
        return r
    
    def get_element(self, element_name, element_id):
        return self.request_get_element(element_name, element_id).json()
    
    @retry_n_times
    def request_get_elements(self, element_name, limit, offset,
                             filters=None, order=None):
        if filters is None:
            filters = []
        parameters = {'limit': limit, 'offset': offset}
        for f in filters:
            parameters.update(f.to_param())
            
        if order is not None:
            parameters['order'] = order

        url = '{}/marketplace/{}s'
        r = requests.get(url.format(self.api_url, element_name),
                         params=parameters, headers=self.auth_header,
                         proxies=self.proxies)
        return r
    
    def get_products(self, limit=100, offset=0, filters=None):
        if filters is None:
            filters = []
        r = self.request_get_elements('product', limit, offset, filters)
        return r.json()
    
    def get_retailers(self, limit=20, offset=0, filters=None):
        if filters is None:
            filters = []
        r = self.request_get_elements('retailer', limit, offset, filters)
        return r.json()

    def request_create_retailer(self, name, url, country):
        data = {'name': name, 'url': url, 'country': country}
        r = requests.post('{}/marketplace/retailers'.format(self.api_url),
                          headers=self.auth_header, json=data,
                          proxies=self.proxies)
        return r
    
    def get_skus(self, limit=20, offset=0, filters=None):
        if filters is None:
            filters = []
        r = self.request_get_elements('stock-keeping-unit', limit,
                                      offset, filters)
        return r.json()

    def request_update_sku_price_offers(self, sku_id, new_price_offers):
        url = '{}/marketplace/stock-keeping-units/{}/price-offers'
        r = requests.put(url.format(self.api_url, sku_id),
                         json=new_price_offers, proxies=self.proxies,
                         headers=self.auth_header)
        return r

    def request_create_sku(self, product_id, number_products, url,
                           retailer_id, image_urls=None):
        data = {'product_id': product_id, 'number_products': number_products,
                'url': url, 'retailer_id': retailer_id}
        if image_urls is not None:
            data['image_urls'] = image_urls

        request_url = '{}/marketplace/stock-keeping-units'
        r = requests.post(request_url.format(self.api_url), json=data,
                          headers=self.auth_header, proxies=self.proxies)
        return r
    
    def request_add_imageurl_to_sku(self, product_id, image_url):
        request_url = '{}/marketplace/stock-keeping-units/{}/image_urls'
        r = requests.post(request_url.format(self.api_url, product_id),
                          headers=self.auth_header, json={'url': image_url},
                          proxies=self.proxies)
        return r
    
    def get_price_offers(self, limit=20, offset=0, filters=None):
        if filters is None:
            filters = []
        r = self.request_get_elements('price-offer', limit, offset, filters)
        return r.json()
    
    def request_create_price_offer(self, sku_id, unit_price, currency,
                                   min_quantity, max_quantity=None):
        data = {'sku_id': sku_id,
                'min_quantity': min_quantity,
                'unit_price': unit_price,
                'currency': currency}
        if max_quantity is not None:
            data['max_quantity'] = max_quantity

        request_url = '{}/marketplace/price-offers'
        r = requests.post(request_url.format(self.api_url), json=data,
                          headers=self.auth_header, proxies=self.proxies)
        return r
    
    def plot_product_price_offers(self, product_id):
        current_time = int(time.time())
        filters = [EqualityFilter('sku.product.id', product_id)]
        price_offers = self.get_all_elements('price_offer', filters)
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
        
        sku_ids = []
        sku_labels = {}
        for price_offer in price_offers:
            sku_id = price_offer['stock_keeping_unit']['id']
            if sku_id not in sku_ids:
                sku_ids.append(sku_id)
        
            if sku_id not in sku_labels:
                sku_labels[sku_id] = '{} SKU {}'.format(self.get_element('stock-keeping-unit', sku_id)['retailer']['name'],
                                               sku_id)
      
        cmap = get_cmap('jet')
        sku_colors = {sku_id: cmap(ii/(len(sku_ids))) for ii, sku_id in enumerate(sku_ids)}
        labelled_sku = []
        handles = []
        labels = []
        for price_offer in price_offers:
            sku_id = price_offer['stock_keeping_unit']['id']
            if price_offer['validity_end'] is None:
                validity_end = current_time
            else:
                validity_end = price_offer['validity_end']
            
            handle, = ax1.plot([price_offer['validity_start'], validity_end],
                    [price_offer['unit_price']]*2,
                    color=sku_colors[sku_id],
                    marker='o')
            ax1.text(0.5*(validity_end+price_offer['validity_start']),
                    price_offer['unit_price'],
                    '{}-{}'.format(price_offer['min_quantity'], price_offer['max_quantity'])
                    )
            if not sku_id in labelled_sku:
                handles.append(handle)
                labels.append(sku_labels[sku_id])
                labelled_sku.append(sku_id)
        ax1.legend(handles, labels)
        ax1.set_title('Price offers')

        ax1.grid(True)
        
        product = self.get_element('product', product_id)
        price_by_qty = {}
        disappered_qty = set()
        for timestamp, price_breaks in product['prices_history']:
            seen_qty_t = set()
            for quantity, unit_price in price_breaks:
                seen_qty_t.add(quantity)
                if quantity in disappered_qty:
                    disappered_qty.remove(quantity)
                if quantity in price_by_qty:
                    price_by_qty[quantity][0].append(timestamp)
                    price_by_qty[quantity][1].append(unit_price)
                else:
                    price_by_qty[quantity] = [[timestamp], [unit_price]]
            
            for quantity in price_by_qty.keys():
                if quantity not in seen_qty_t:
                    disappered_qty.add(quantity)

            for quantity in disappered_qty:
                price_by_qty[quantity][0].append(timestamp)                    
                price_by_qty[quantity][1].append(None)                    

        for quantity, (x, y) in price_by_qty.items():
            if y[-1] is not None:
                x.append(current_time)
                y.append(y[-1])

        nqty = len(price_by_qty)
        for iq, (quantity, (x, y)) in enumerate(price_by_qty.items()):
            color = cmap(iq/nqty)
            ax2.step(x, y, where='post', label='For {}'.format(quantity),
                     color=color)
            ax2.plot(x, y, 'o', color=color)
            
        ax2.set_title('Global price history')
        
        ax2.legend()
                    
        ax1.grid(True)
        ax2.grid(True)
        
    def get_applications(self):
        return requests.get('{}/applications'.format(self.api_url),
                            headers=self.auth_header, proxies=self.proxies)

    def my_network(self):
        return requests.get('{}/account/network'.format(self.api_url),
                            headers=self.auth_header, proxies=self.proxies)


class AdminClient(Client):
    def __init__(self, username=None, password=None, token=None, proxies=None,
                 api_url='https://api.platform.dessia.tech',
                 max_retries=10, retry_interval=2):
        Client.__init__(self, username=username, password=password,
                        token=token, proxies=proxies, api_url=api_url,
                        max_retries=max_retries, retry_interval=retry_interval)

    def status(self):
        r = requests.get('{}/admin/status'.format(self.api_url),
                         headers=self.auth_header, proxies=self.proxies)
        return r

    def get_config(self):
        r = requests.get('{}/admin/config'.format(self.api_url),
                         headers=self.auth_header,
                         proxies=self.proxies)
        return r

    def update_config(self, update_dict):
        r = requests.post('{}/admin/config'.format(self.api_url),
                          json=update_dict,
                          headers=self.auth_header,
                          proxies=self.proxies)
        return r

    def import_errors(self):
        r = requests.get('{}/admin/import-errors'.format(self.api_url),
                         headers=self.auth_header, proxies=self.proxies)
        return r
    
    def refresh_models(self):
        r = requests.get('{}/admin/models/refresh'.format(self.api_url),
                         headers=self.auth_header, proxies=self.proxies)
        return r
    
    def error_objects(self):
        r = requests.get('{}/objects/errors'.format(self.api_url),
                         headers=self.auth_header, proxies=self.proxies)
        return r
        
    def inspect_objects(self, max_duration=60.):
        r = requests.get('{}/objects/inspect'.format(self.api_url),
                         params={'max_duration': max_duration},
                         headers=self.auth_header, proxies=self.proxies)
        return r
    
    def logs(self, limit=50, offset=0):
        r = requests.get('{}/admin/logs'.format(self.api_url),
                         params={'limit': limit, 'offset': offset},
                         headers=self.auth_header, proxies=self.proxies)
        return r
    
    def auth_logs(self, limit=50, offset=0):
        r = requests.get('{}/admin/logs/auth'.format(self.api_url),
                         params={'limit': limit, 'offset': offset},
                         headers=self.auth_header, proxies=self.proxies)
        return r
    
    def hash_warnings(self, limit=50, offset=0):
        r = requests.get('{}/admin/objects/hash-warnings'.format(self.api_url),
                         headers=self.auth_header, proxies=self.proxies)
        return r

    def object_stats(self):
        r = requests.get('{}/objects/stats'.format(self.api_url),
                         headers=self.auth_header, proxies=self.proxies)
        return r

    def update_application(self, application_id: int,
                           name: str = None, active: bool = None,
                           installed_distribution_id: int = None):
        data = {}
        if name:
            data['name'] = name
        if active:
            data['active'] = active
        if installed_distribution_id:
            data['installed_distribution_id'] = installed_distribution_id
        if not data:
            print('Empty data, no need to fire a request')
            return None

        url = '{}/applications/{}'
        return requests.post(url.format(self.api_url, application_id),
                             headers=self.auth_header, proxies=self.proxies,
                             json=data)

    def delete_application(self, application_id: int):
        url = '{}/applications/{}'
        return requests.delete(url.format(self.api_url, application_id),
                               headers=self.auth_header, proxies=self.proxies)

    def upload_file_distribution(self, distribution_filepath):
        files = {'file': open(distribution_filepath, 'rb')}
        url = '{}/file-application-distributions'
        return requests.post(url.format(self.api_url), proxies=self.proxies,
                             headers=self.auth_header, files=files)

    def create_git_distribution(self, http_url, username, token):
        data = {'http_url': http_url, 'username': username, 'token': token}
        url = '{}/git-application-distributions'
        return requests.post(url.format(self.api_url), proxies=self.proxies,
                             headers=self.auth_header, json=data)

    def delete_distribution(self, distribution_id: int):
        url = '{}/application-distributions/{}'
        return requests.delete(url.format(self.api_url, distribution_id),
                               headers=self.auth_header, proxies=self.proxies)
    
    def update_user(self, user_id: int, first_name: str = None,
                    last_name: str = None, active: bool = None,
                    admin: bool = None):
        arguments = {'first_name': first_name, 'last_name': last_name,
                     'active': active, 'admin': admin}
        data = {k: v for k, v in arguments.items() if v is not None}
        if not data:
            print('Empty data, no need to fire a request')
            return None

        url = '{}/admin/users/{}'
        return requests.post(url.format(self.api_url, user_id), json=data,
                             headers=self.auth_header, proxies=self.proxies)

    def add_computation_usage(self, owner: str, time: float):
        data = {'owner': owner, 'time': time}
        url = '{}/admin/computation-usage'
        return requests.post(url.format(self.api_url), proxies=self.proxies,
                             headers=self.auth_header, json=data)

    def stats(self):
        return requests.get('{}/admin/stats'.format(self.api_url),
                             headers=self.auth_header,
                             proxies=self.proxies)

    def edit_style(self, *,
                   logo_filename:str=None,
                   logo_small_filename:str=None,
                   favicon_filename:str=None):
        files = {}
        for filename, value in [('logo', logo_filename),
                                ('logo-small', logo_small_filename),
                                 ('favicon', favicon_filename)]:
            if value is not None:
                files = {filename: open(value, 'rb')}
        if not files:
            print('Nothing to upload')
            return None
        return requests.post('{}/style'.format(self.api_url),
                             headers=self.auth_header,
                             proxies=self.proxies,
                             files=files)
