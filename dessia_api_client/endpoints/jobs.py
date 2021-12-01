"""
/jobs
/jobs/finished
/jobs/running
/jobs/submit
/jobs/{job_id}
/jobs/{job_id}
"""

from dessia_api_client.clients import PlatformApiClient


class Jobs:
    def __init__(self, client: PlatformApiClient):
        self.client = client

    def job_details(self, job_id: int):
        return self.client.get('/jobs/{job_id}',
                               path_subs={'job_id': job_id})

    def list_jobs(self):
        return self.client.get('/jobs')

    def finished_jobs(self):
        return self.client.get('/jobs/finished')

    def running_jobs(self):
        return self.client.get('/jobs/running')

    def submit_job(self, object_class, object_id):
        return self.client.post('/jobs',
                                json={'object_class': object_class,
                                      "object_id": object_id})

    def delete_job(self, job_id):
        return self.client.delete('/jobs/{job_id}',
                                  path_subs={'job_id': job_id})
