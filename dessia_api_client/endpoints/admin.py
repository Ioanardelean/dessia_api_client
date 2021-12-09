"""
/admin/organizations/infos
/admin/applications/errors
/admin/migration/import
/admin/objects/hash-warnings
/admin/workers/restart
/admin/models/refresh
/admin/users/infos
/admin/logs/auth

/admin/computation_usage
/admin/python-packages
/admin/organizations
/admin/email-test
/admin/activity
/admin/restart
/admin/status
/admin/system
/admin/config
/admin/config
/admin/users
/admin/stats
/admin/logs
/admin/jobs

/admin/users/{user_id}/password/reset-code
/admin/logs/auth/{log_id}
/admin/users/{user_id}
/admin/users/{user_id}
/admin/logs/{log_id}

"""

from dessia_api_client.utils.helpers import confirm
from dessia_api_client.clients import PlatformApiClient


class Admin:
    def __init__(self, client: PlatformApiClient):
        self.client = client

    def status(self):
        return self.client.get('/admin/status')

    def get_config(self):
        return self.client.get('/admin/config')

    def update_config(self, update_dict):
        return self.client.post('admin/config',
                                json=update_dict)

    def import_errors(self):
        return self.client.get('/admin/import-errors')

    def refresh_models(self):
        return self.client.get('/admin/models/refresh')

    def error_objects(self):
        return self.client.get('/objects/errors')

    def inspect_objects(self, max_duration=60.):
        return self.client.get('/objects/inspect',
                               params={'max_duration': max_duration})

    def logs(self, limit=50, offset=0):
        return self.client.get('/admin/logs',
                               params={'limit': limit, 'offset': offset})

    def auth_logs(self, limit=50, offset=0):
        return self.client.get('/admin/logs/auth',
                               params={'limit': limit, 'offset': offset})

    def hash_warnings(self):
        return self.client.get('/admin/objects/hash-warnings')

    def object_stats(self):
        return self.client.get('/objects/stats')

    def update_application(self, application_id: int,
                           name: str = None, active: bool = None,
                           installed_distribution_id: int = None):

        return self.client.post('/applications/{application_id}',
                                path_subs={'application_id': application_id},
                                json={"name": name,
                                      "active": active,
                                      "installed_distribution_id": installed_distribution_id
                                      })

    def update_user(self, user_id: int, first_name: str = None,
                    last_name: str = None, active: bool = None,
                    admin: bool = None):
        data = {'first_name': first_name,
                'last_name': last_name,
                'active': active,
                'admin': admin}

        return self.client.post(
            '/admin/users/{user_id}',
            path_subs={'user_id': user_id},
            json=data
        )

    def add_computation_usage(self, owner: str, time: float):
        return self.client.post('/admin/computation-usage',
                                json={'owner': owner, 'time': time})

    def stats(self):
        return self.client.get('/admin/stats')

    def edit_style(self,
                   logo_filename: str = None,
                   logo_small_filename: str = None,
                   favicon_filename: str = None):
        files = {}
        for filename, value in [('logo', logo_filename),
                                ('logo-small', logo_small_filename),
                                ('favicon', favicon_filename)]:
            if value is not None:
                files = {filename: open(value, 'rb')}

        return self.client.post('/style',
                                files=files)

    def delete_public_objects(self, interactive: bool = True):
        if not interactive or confirm('Deletion', 'This will delete all public objects from database.'):
            return self.client.delete('/objects')

    def upload_file(self, filepath):
        return self.client.post('/files',
                                files={'file': open(filepath, 'rb')})
