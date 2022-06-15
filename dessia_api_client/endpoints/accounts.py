"""
/account/workspaces/joinable
/account/password/reset-email
/account/password/reset
/account/verify
/account/infos
/account/password
/account/network
/account/token-refresh
/account/send-verification-code
/technical_accounts/create


/users
/auth

/users/{user_id}/avatar.png


"""

from dessia_api_client.clients import PlatformApiClient


class Accounts:
    def __init__(self, client: PlatformApiClient):
        self.client = client

    def create_user(self, email, password, first_name, last_name):
        return self.client.post('/users',
                                json={'email': email,
                                      'password': password,
                                      'first_name': first_name,
                                      'last_name': last_name},
                                auth=False)

    def send_verification_email(self, email):
        return self.client.get('/account/send-verification-code',
                               params={'email': email})

    def my_network(self):
        return self.client.get('/account/network')

    def verify_email(self, token):
        return self.client.post('/account/verify',
                                json={'token': token})

    def request_my_account(self):
        return self.client.get('/account/infos')
