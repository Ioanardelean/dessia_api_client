"""

/applications/active
/applications
/applications/{application_id}/logo
/applications/{application_id}
/applications/{application_id}

"""

from dessia_api_client.clients import PlatformApiClient


class Applications:
    def __init__(self, client: PlatformApiClient):
        self.client = client

    def get_active_applications(self):
        return self.client.get('/applications/active')

    def get_all_applications(self):
        return self.client.get('/applications')

    def get_application_logo(self, application_id):
        return self.client.get('/applications/{application_id}/logo',
                               path_subs={"application_id": application_id})

    def update_application(self, application_id):
        return self.client.post('/applications/{application_id}',
                                path_subs={"application_id": application_id})

    def delete_application(self, application_id):
        return self.client.delete('/applications/{application_id}',
                                  path_subs={"application_id": application_id})
