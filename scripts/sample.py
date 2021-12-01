from dessia_api_client.users import PlatformUser

# get an api user
# replace with proper credentials
brad = PlatformUser("brad@dessia.tech", "brad_pass1!", api_url="https://api.platform.dessia.tech")

# run your tests/scripts
# for eg:
all_jobs_resp = brad.jobs.list_jobs()  # list jobs
brad.jobs.submit_job(object_class="some_class", object_id=5)  # submit new one
active_apps = brad.applications.get_active_applications()  # see active apps ...
