from factory import TestFactory
from dessia_api_client.utils.helpers import validate_status_code
import logging


def basic_objects_tests():
    logging.info('running basic_objects_tests')
    user = TestFactory.get_user()
    resp = user.objects.get_object_classes()
    validate_status_code(resp, 200)

    resp = user.objects.get_class_hierarchy()
    validate_status_code(resp, 200)

    resp = user.objects.get_all_class_objects("non_existing_class")
    validate_status_code(resp, 404)


if __name__ == '__main__':
    basic_objects_tests()
