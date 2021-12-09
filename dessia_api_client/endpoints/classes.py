"""

/classes/tree
/classes/{object_class}/subclasses
/classes/{classname}/jsonschema
/classes/{classname}/members
/classes/{object_class}

"""

from dessia_api_client.clients import PlatformApiClient


class ClassesEndPoint:
    def __init__(self, client:PlatformApiClient):
        self.client = client

    def get_subclasses(self, object_class: str):
        return self.client.get('/classes/{object_class}/subclasses',
                                path_subs={'object_class': object_class})