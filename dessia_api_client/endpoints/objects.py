"""
/objects/class_hierarchy
/objects/instantiate
/objects/classes
/objects/inspect
/objects/public
/objects/errors
/objects/stats
/objects

/objects/{object_class}/default_dict
/objects/{object_class}/attributes
/objects/{class_name}/logo.{extension}
/objects/{object_class}/list
/objects/{object_class}/{object_id}/method_attributes
/objects/{object_class}/{object_id}/object_display
/objects/{object_class}/{object_id}/replace
/objects/{object_class}/{object_id}/export/{export_format}
/objects/{object_class}/{object_id}/copy
/objects/{object_class}/{object_id}/{path}
/objects/{object_class}/{object_id}
/objects/{object_class}/{object_id}
/objects/{object_class}/{object_id}
/objects/{object_class}/{object_id}
/objects/{object_class}
/objects/{object_class}


/object-inserts/{task_id}

"""

import time
import simplejson.errors
import jwt
import time
import getpass
import warnings
import requests
import matplotlib.pyplot as plt
from dessia_api_client.utils.helpers import stringify_dict_keys, instantiate_object, confirm
from dessia_api_client.utils.filters import EqualityFilter
from dessia_api_client.clients import PlatformApiClient
from matplotlib.cm import get_cmap

try:
    import dessia_common as dc
except ModuleNotFoundError:
    msg = 'Dessia common module could not be found.\n'
    msg += 'It is required for object handling.'
    print()


class ObjectsEndPoint:
    def __init__(self, client: PlatformApiClient):
        self.client = client

    def get_object_classes(self):
        return self.client.get('/objects/classes')

    def get_class_hierarchy(self):
        return self.client.get('/objects/class_hierarchy')

    def get_object_plot_data(self, object_class, object_id):
        return self.client.get('/objects/{object_class}/{object_id}/plot-data',
                               path_subs={'object_class': object_class,
                                          'object_id': object_id})

    def get_all_class_objects(self, object_class):
        return self.client.get('/objects/{object_class}',
                               path_subs={'object_class': object_class})

    def object_display(self, object_class, object_id):
        return self.client.get('/objects/{object_class}/{object_id}/object_display',
                               path_subs={'object_class': object_class,
                                          'object_id': object_id})

    def get_subobject(self, object_class: str,
                      object_id: str,
                      deep_attribute: str = None,
                      instantiate: bool = True):

        payload = {'embedded_subobjects': str(instantiate).casefold()}

        req = self.client.get(f'/objects/{object_class}/{object_id}/{deep_attribute}',
                              params=payload)
        if instantiate:
            result = req.json()
            if dc.is_sequence(result):
                return [instantiate_object(v) for v in result]
            else:
                return instantiate_object(result)
        return req

    def _wait_for_object_created(self, payload):
        r = self.client.post('/objects',
                             json=payload)
        try:
            rj = r.json()
        except simplejson.errors.JSONDecodeError:
            print(r.text)
            return r
        
        if 'task_id' not in rj:
            return r
        
        task_id = rj['task_id']
        while r.status_code != 201:
            print(r.text)
            print('retrying to see if object was inserted')
            r = self.client.get(f'/object-inserts/{task_id}')
            time.sleep(2.)

        return r

    def create_object_from_python_object(self, obj, owner=None,
                                         embedded_subobjects=True,
                                         public=False):
        try:
            dict_ = obj.to_dict(use_pointers=True)
        except TypeError:
            dict_ = obj.to_dict()

        payload = {
            'object': {
                'object_class': '{}.{}'.format(obj.__class__.__module__,
                                               obj.__class__.__name__),
                'json': stringify_dict_keys(dict_)
            },
            'embedded_subobjects': embedded_subobjects,
            'public': public}
        if owner is not None:
            payload['owner'] = owner

        return self._wait_for_object_created(payload)

    def create_object_from_object_dict(self, object_dict, owner=None,
                                       embedded_subobjects=True, public=False):
        payload = {'object': {'object_class': object_dict['object_class'],
                              'json': stringify_dict_keys(object_dict)},
                   'embedded_subobjects': embedded_subobjects,
                   'public': public}
        if owner is not None:
            payload['owner'] = owner

        return self._wait_for_object_created(payload)

    def replace_object(self, object_class, object_id, new_object,
                       embedded_subobjects: bool = False, owner=None):

        data = {'object': {'object_class': object_class,
                           'json': stringify_dict_keys(new_object.to_dict())},
                'embedded_subobjects': embedded_subobjects,
                'owner': owner}

        return self.client.post('/objects/{object_class}/{object_id}/replace',
                                path_subs={'object_id': object_id,
                                           'object_class': object_class},
                                json=data)

    def update_object(self, object_class, object_id, update_dict):
        return self.client.post('/objects/{object_class}/{object_id}/update',
                                path_subs={'object_class': object_class,
                                           'object_id': object_id},
                                json=update_dict)

    def delete_object(self, object_class, object_id):
        return self.client.delete('/objects/{object_class}/{object_id}',
                                  path_subs={'object_class': object_class, 'object_id': object_id})

    def delete_all_objects_from_class(self, object_class='', interactive: bool = True):
        objects = self.get_all_class_objects(object_class).json()
        if not interactive or confirm('Deletion',
                                      'This will delete {} objects from class {}'.format(len(objects), object_class)):
            return self.client.delete('/objects/{object_class}', path_subs={'object_class': object_class})

    def delete_all_objects(self, interactive: bool = True):
        if not interactive or confirm('Deletion',
                                      'This will delete all objects from database'):
            return self.client.delete('/objects')

    def method_attributes(self, object_class, object_id):
        return self.client.get('/objects/{object_class}/{object_id}/method_attributes',
                               path_subs={'object_class': object_class,
                                          'object_id': object_id})

    def get_class_attributes(self, class_):
        """
        Gets class attributes
        (_standalone_in_db, _jsonschema, and other class data)
        """
        return self.client.get('/objects/{class_}/attributes',
                               path_subs={'class_': class_})

    def get_object(self, object_class: str, object_id: str,
                   instantiate: bool = True, embedded_subobjects=True):
        if instantiate and not embedded_subobjects:
            raise ValueError('embedded_subobjects must be set to True when instantiating')
        payload = {'embedded_subobjects': str(embedded_subobjects).casefold()}

        r = self.client.get('/objects/{object_class}/{object_id}',
                            params=payload,
                            path_subs={'object_id': object_id, 'object_class': object_class})
        if instantiate and r.status_code == 200:
            return instantiate_object(r.json())
        return r

    def object_method(self, object_class, object_id, method, arguments=None):
        if arguments is None:
            arguments = {}
        serialized_arguments = dc.serialize_dict(arguments)
        data = {'object': {'object_class': object_class,
                           'object_id': object_id},
                'method': method,
                'method_dict': serialized_arguments}
        return self.client.post('/jobs/submit',
                                json=data)
