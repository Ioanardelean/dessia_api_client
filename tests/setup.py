from dessia_api_client.users import GenericUser
from dessia_api_client.utils.helpers import validate_status_code
import os


class TestFactory:
    TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL')
    TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD')
    TEST_API_URL = os.getenv('TEST_API_URL', 'https://api.platform.dessia.tech')
    TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    _user = None

    @classmethod
    def get_user(cls):
        if cls._user is None:
            cls._user = GenericUser(email=cls.TEST_USER_EMAIL,
                                    password=cls.TEST_USER_PASSWORD,
                                    api_url=cls.TEST_API_URL)
        return cls._user
