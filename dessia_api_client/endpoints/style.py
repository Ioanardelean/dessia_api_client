"""

/style/{image_name}
/style

"""

from dessia_api_client.clients import ApiClient


class Styles:
    def __init__(self, client: ApiClient):
        self.client = client
