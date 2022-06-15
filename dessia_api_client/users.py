# import os
# import jwt
# import time
# import requests

from dessia_api_client.endpoints import admin, jobs, accounts, applications, files, objects, style, \
    marketplace, organisations, classes, distributions
from dessia_api_client.clients import PlatformApiClient


class PlatformUser:
    def __init__(self,
                 email=None,
                 password=None,
                 api_url="https://api.platform.dessia.tech",
                 max_retries=3,
                 retry_interval=3):
        """
        :param email:
        :param password:
        :param api_url:
        :param max_retries:
        :param retry_interval:
        """

        self.client = PlatformApiClient(email, password,
                                        api_url=api_url,
                                        max_retries=max_retries,
                                        retry_interval=retry_interval)
        self.jobs = jobs.Jobs(self.client)
        self.admin = admin.Admin(self.client)
        self.account = accounts.Accounts(self.client)
        self.applications = applications.Applications(self.client)
        self.distributions = distributions.Distributions(self.client)
        self.classes = classes.ClassesEndPoint(self.client)
        self.files = files.Files(self.client)
        self.marketplace = marketplace.Marketplace(self.client)
        self.objects = objects.ObjectsEndPoint(self.client)
        self.organisations = organisations.Organisations(self.client)
        self.style = style.Styles(self.client)
