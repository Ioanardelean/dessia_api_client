"""

/classes/tree
/classes/{object_class}/subclasses
/classes/{classname}/jsonschema
/classes/{classname}/members
/classes/{object_class}

"""

from dessia_api_client.clients import ApiClient


class ClassesEndPoint:
    def __init__(self, client):
        self.client = client
