"""

/files/{file_id}
/files

"""

from dessia_api_client.clients import PlatformApiClient


class Files:
    def __init__(self, client: PlatformApiClient):
        self.client = client

    def list_files(self):
        return self.client.get('/files')

    def create_file(self, file_path):
        return self.client.post('/files',
                                files={'file': open(file_path, 'rb')})

    def get_file(self, file_id):
        return self.client.get('/files/{file_id}',
                               path_subs={'file_id': file_id})

    def delete_file(self, file_id):
        return self.client.delete('/files/{file_id}',
                                  path_subs={'file_id': file_id})
