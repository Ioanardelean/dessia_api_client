import requests
import os

import importlib
import random
import string

import time

import requests
from .exceptions import APIConnectionError


def validate_status_code(response: requests.Response, expected_code):
    assert response.status_code == expected_code, \
        f'Expected status code was {expected_code}, instead we got : {response.status_code} \n {response.content}'


def stringify_dict_keys(d):
    if type(d) == list or type(d) == tuple:
        new_d = []
        for di in d:
            new_d.append(stringify_dict_keys(di))

    elif type(d) == dict:
        new_d = {}
        for k, v in d.items():
            new_d[str(k)] = stringify_dict_keys(v)
    else:
        return d
    return new_d


def instantiate_object(json):
    module_name, class_name = json['object_class'].rsplit('.', 1)
    module = importlib.import_module(module_name)
    object_class = getattr(module, class_name)
    return object_class.dict_to_object(json['object_dict'])


def confirm(action: str = 'Action', message=None):
    if message:
        print(message)
    validator = ''.join(random.choices(string.ascii_uppercase, k=6))
    print('Confirm by typing in following code : {}'.format(validator))
    print('Let empty to abort.\n')
    validation = input('> ')
    if validation == validator:
        return True
    elif not validation:
        print('\n{} aborted'.format(action))
        return False
    else:
        print('\nInput did not match validator. {} aborted'.format(action))
        return False


def retry_n_times(func):
    def func_wrapper(self, *args, **kwargs):
        connection_error = True
        n_tries = 1
        while connection_error and (n_tries <= self.max_retries):
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
            raise APIConnectionError('Retried {} times, API is not reachable'.format(self.max_retries))
        else:
            return r

    return func_wrapper
