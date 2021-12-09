"""
/file-application-distributions
/git-application-distributions
/pip-application-distributions

/application-distributions/{distribution_id}

"""

from dessia_api_client.clients import PlatformApiClient


class Distributions:
    def __init__(self, client: PlatformApiClient):
        self.client = client

    def create_file_distribution(self, file_path):
        return self.client.post('/file-application-distributions',
                                files={'file': open(file_path, 'rb')})

    def create_git_distribution(self, http_url, username, token, branch=None, commit=None):
        return self.client.post('/git-application-distributions',
                                json={'http_url': http_url,
                                      'username': username,
                                      'token': token,
                                      'current_branch': branch,
                                      'current_commit': commit})

    def create_pip_distribution(self, dist_name, dist_version=None):
        return self.client.post('/pip-application-distributions',
                                json={'name': dist_name,
                                      'version': dist_version})

    def delete_distribution(self, dist_id):
        return self.client.delete('/application-distributions/{dist_id}',
                                  path_subs={"dist_id": dist_id})


