from setup import TestFactory
from dessia_api_client.utils.helpers import validate_status_code
import logging


def basic_jobs_tests():
    logging.info('running basic_jobs_tests')
    user = TestFactory.get_user()

    resp = user.jobs.job_details(-14)  # non existing job
    validate_status_code(resp, 404)

    resp = user.jobs.list_jobs()
    validate_status_code(resp, 200)
    assert resp.json() == []


if __name__ == '__main__':
    basic_jobs_tests()
