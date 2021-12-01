"""

/workspaces/{workspace_id}/users/{user_id}/accept
/workspaces-invitations/{invitation_id}/accept

/workspaces/{workspace_id}/shared-objects
/workspaces/{workspace_id}/shared-objects
/workspaces/{workspace_id}/invitations
/workspaces/{workspace_id}/avatar.png
/workspaces/{workspace_id}/documents
/workspaces/{workspace_id}/messages
/workspaces/{workspace_id}/messages
/workspaces/{workspace_id}/events
/workspaces/{workspace_id}/images
/workspaces/{workspace_id}/leave
/workspaces/{workspace_id}/join
/workspaces/{workspace_id}
/workspaces/{workspace_id}
/workspaces/{workspace_id}

/workspaces-invitations/{invitation_id}

/message-attachments/{attachment_id}


"""

from dessia_api_client.clients import PlatformApiClient


class Workspaces:
    def __init__(self, client: PlatformApiClient):
        self.client = client

    def get_workspace(self, workspace_id: int):
        return self.client.get('/workspaces/{workspace_id}',
                               path_subs={'workspace_id': workspace_id})
