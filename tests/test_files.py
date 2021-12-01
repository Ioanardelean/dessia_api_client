from setup import TestFactory
from dessia_api_client.utils.helpers import validate_status_code
import os
import logging


def basic_files_upload_tests():
    logging.info('running basic_files_upload_tests')
    user = TestFactory.get_user()

    resp = user.files.list_files()
    validate_status_code(resp, 200)

    origin_files_ids = [x['id'] for x in resp.json()]
    new_file_name = 'sample_file.txt'
    resp = user.files.create_file(os.path.join(TestFactory.TEST_DATA_DIR, new_file_name))
    validate_status_code(resp, 201)

    resp = user.files.list_files()
    new_file = [x for x in resp.json() if x not in origin_files_ids][0]
    assert new_file["name"] == new_file_name

    resp = user.files.get_file(file_id=new_file["id"])
    file_lines = str(resp.content.decode('utf-8'))
    uploaded_file_lines = open(os.path.join(TestFactory.TEST_DATA_DIR, new_file_name)).read()
    assert file_lines == uploaded_file_lines

    resp = user.files.delete_file(file_id=new_file["id"])
    assert resp.status_code == 200

    resp = user.files.list_files()
    saved_files_ids = [x["id"] for x in resp.json()]
    assert new_file["id"] not in saved_files_ids


if __name__ == '__main__':
    basic_files_upload_tests()
