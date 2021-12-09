from factory import TestFactory
from dessia_api_client.utils.helpers import validate_status_code
import os
import logging


def basic_users_test():
    logging.info('running basic_files_upload_tests')
    user = TestFactory.get_user()
    print(user.client.token)


if __name__ == '__main__':
    basic_users_test()
