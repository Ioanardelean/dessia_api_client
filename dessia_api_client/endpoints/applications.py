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

    def update_application(self, application_id, name=None, active=None, installed_distribution_id=None):
        payload = {}
        if name is not None:
            payload['name'] = name
        if active is not None:
            payload['active'] = active
        if installed_distribution_id is not None:
            payload['installed_distribution_id'] = installed_distribution_id
        if not payload:
            raise ValueError('Empty payload for request')
        return self.client.post('/applications/{application_id}',
                                path_subs={"application_id": application_id},
                                json=payload)

    def delete_application(self, application_id):
        return self.client.delete('/applications/{application_id}',
                                  path_subs={"application_id": application_id})
