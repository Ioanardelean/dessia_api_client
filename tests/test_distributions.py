from factory import TestFactory
from dessia_api_client.utils.helpers import validate_status_code
import os
import logging


def test_install_from_wheel():
    logging.info('running test_install_from_wheel')
    user = TestFactory.get_user()

    # delete existing apps
    resp = user.applications.get_all_applications()
    for app in resp.json():
        resp = user.applications.delete_application(app["id"])
        validate_status_code(resp, 200)

    # create wheel dist
    resp = user.distributions.create_file_distribution(
        os.path.join(TestFactory.TEST_DATA_DIR,
                     'genmechanics-0.1.6-py3-none-any.whl'))
    validate_status_code(resp, 201)

    resp = user.applications.get_all_applications()
    wheel_dist = resp.json()[0]["distributions"][0]
    assert wheel_dist["application"]["package_name"] == "genmechanics"
    assert wheel_dist["type"] == "wheel"

    # validate no app is installed
    assert "installed_distribution" not in resp.json()[0]

    # delete dists is ok
    user.distributions.delete_distribution(wheel_dist['id'])
    validate_status_code(resp, 200)


def test_install_from_pip():
    logging.info('running test_install_from_pip')
    user = TestFactory.get_user()

    # delete existing apps
    resp = user.applications.get_all_applications()
    for app in resp.json():
        resp = user.applications.delete_application(app["id"])
        validate_status_code(resp, 200)

    # create pip dist
    resp = user.distributions.create_pip_distribution(dist_name='volmdlr')
    validate_status_code(resp, 201)

    resp = user.applications.get_all_applications()
    pip_dist = resp.json()[0]["distributions"][0]
    assert pip_dist["application"]["package_name"] == "volmdlr"
    assert pip_dist["type"] == "pip"

    # validate no app is installed
    assert "installed_distribution" not in resp.json()[0]

    # delete dists is ok
    user.distributions.delete_distribution(pip_dist['id'])
    validate_status_code(resp, 200)


def test_install_from_archive():
    logging.info('running test_install_from_wheel')
    user = TestFactory.get_user()

    # delete existing apps
    resp = user.applications.get_all_applications()
    for app in resp.json():
        resp = user.applications.delete_application(app["id"])
        validate_status_code(resp, 200)

    # install targz dist
    resp = user.distributions.create_file_distribution(os.path.join(TestFactory.TEST_DATA_DIR, 'volmdlr-0.2.10.tar.gz'))
    validate_status_code(resp, 201)
    user.applications.delete_application(resp.json()['application']['id'])

    # install zip dist
    resp = user.distributions.create_file_distribution(os.path.join(TestFactory.TEST_DATA_DIR, 'volmdlr-0.2.10.zip'))
    validate_status_code(resp, 201)
    user.applications.delete_application(resp.json()['application']['id'])


def test_install_from_git():
    logging.info('running test_install_from_git')
    user = TestFactory.get_user()

    # delete existing apps
    resp = user.applications.get_all_applications()
    for app in resp.json():
        resp = user.applications.delete_application(app["id"])
        validate_status_code(resp, 200)

    # create pip dist
    resp = user.distributions.create_git_distribution('https://github.com/ladnane/tutodessia',
                                                      'ladnane',
                                                      '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')
    validate_status_code(resp, 201)

    resp = user.applications.get_all_applications()
    pip_dist = resp.json()[0]["distributions"][0]
    assert pip_dist["application"]["package_name"] == "adnane_bot"
    assert pip_dist["type"] == "git"

    # validate no app is installed
    assert "installed_distribution" not in resp.json()[0]

    # delete dists is ok
    # user.distributions.delete_distribution(pip_dist['id'])
    validate_status_code(resp, 200)


if __name__ == '__main__':
    test_install_from_wheel()
    test_install_from_pip()
    test_install_from_archive()
    test_install_from_git()
