"""

/organizations-invitations/{invitation_id}/accept
/organizations/{organization_id}/invitations
/organizations/{organization_id}/avatar.png
/organizations/{organization_id}/workspaces
/organizations/{organization_id}/workspaces
/organizations

/organizations-invitations/{invitation_id}
/organizations/{organization_id}

"""

from dessia_api_client.clients import PlatformApiClient


class Organisations:
    def __init__(self, client: PlatformApiClient):
        self.client = client

    def get_organization(self, organization_id: int):
        return self.client.get('/organizations/{organization_id}',
                               path_subs={'organization_id': organization_id})

    def create_organization(self, name: str, type_: str):
        return self.client.post('/organizations',
                                json={'name': name,
                                      'type': type_})

    def create_workspace(self, name: str, organization_id: int):
        return self.client.post('/organizations/{organization_id}/workspaces',
                                path_subs={'organization_id': organization_id},
                                json={'name': name})
