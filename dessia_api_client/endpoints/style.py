"""

/style/{image_name}
/style

"""

from dessia_api_client.clients import PlatformApiClient


class Styles:
    def __init__(self, client: PlatformApiClient):
        self.client = client
