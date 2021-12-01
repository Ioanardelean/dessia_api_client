import os
import jwt
import time
import requests
from requests import Response

from dessia_api_client.utils.helpers import retry_n_times
from urllib.parse import urljoin


class PlatformApiClient:
    def __init__(self, email, password,
                 api_url="https://api.platform.dessia.tech",
                 max_retries=10,
                 retry_interval=3):
        """
        :param email:
        :param password:
        :param api_url: optional
        :param max_retries: optional
        :param retry_interval: optional
        """
        self.password = password
        self.email = email
        self.api_url = api_url
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self._token = None
        self._token_expiration_time = 0

    @property
    def token(self):
        if (self._token is None) or (self._token_expiration_time and self._token_expiration_time < time.time()):
            r = requests.post(urljoin(self.api_url, 'auth'),
                              json={"username": self.email,
                                    "password": self.password}
                              )
            assert r.status_code == 200, f'Failed Authentication from email : {self.email}'
            self._token = r.json()['access_token']
            self._token_expiration_time = jwt.decode(self.token, options={"verify_signature": False})['exp']
        return self._token

    @retry_n_times
    def generic_request(self, method, path,
                        path_subs=None,
                        json=None,
                        params=None,
                        files=None,
                        **kwargs):
        headers = {f'Authorization': f'Bearer {self.token}'}
        real_path = path
        if path_subs:
            for param, value in path_subs.items():
                real_path = real_path.replace('{' + param + '}', str(value))

        if json:
            if isinstance(json, dict):
                json = {k: v for k, v in json.items() if v is not None}

        r = requests.request(method.lower(),
                             urljoin(self.api_url, real_path),
                             headers=headers,
                             json=json,
                             params=params,
                             files=files,
                             **kwargs)

        return r

    # this is repetitive but allow linting with IDE
    def get(self, path, path_subs=None, json=None, params=None, files=None, **kwargs) -> Response:
        return self.generic_request('get', path,
                                    path_subs=path_subs,
                                    json=json,
                                    params=params,
                                    files=files,
                                    **kwargs)

    def post(self, path, path_subs=None, json=None, params=None, files=None, **kwargs) -> Response:
        return self.generic_request('post', path,
                                    path_subs=path_subs,
                                    json=json,
                                    params=params,
                                    files=files,
                                    **kwargs)

    def put(self, path, path_subs=None, json=None, params=None, files=None, **kwargs) -> Response:
        return self.generic_request('put', path,
                                    path_subs=path_subs,
                                    json=json,
                                    params=params,
                                    files=files,
                                    **kwargs)

    def delete(self, path, path_subs=None, json=None, params=None, files=None, **kwargs) -> Response:
        return self.generic_request('delete', path,
                                    path_subs=path_subs,
                                    json=json,
                                    params=params,
                                    files=files,
                                    **kwargs)
