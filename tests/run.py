import test_jobs
import test_files
import test_distributions
import test_marketplace
import test_objects
import logging

logging.getLogger().level = logging.INFO

test_jobs.basic_jobs_tests()
test_files.basic_files_upload_tests()
test_distributions.basic_wheel_pip_dist_tests()
test_marketplace.basic_marketplace_tests()
test_objects.basic_objects_tests()
