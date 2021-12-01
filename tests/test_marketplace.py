from setup import TestFactory
from dessia_api_client.utils.helpers import validate_status_code
import logging


def basic_marketplace_tests():
    logging.info('running basic_marketplace_tests')
    user = TestFactory.get_user()
    resp = user.marketplace.request_marketplace_stats()
    validate_status_code(resp, 200)

    resp = user.marketplace.get_brands()
    validate_status_code(resp, 200)

    resp = user.marketplace.create_product('name', 'url', brand_id=1, object_id=2, object_class='wrong_class')
    assert resp.status_code != 500


if __name__ == '__main__':
    basic_marketplace_tests()
