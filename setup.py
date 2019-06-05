# -*- coding: utf-8 -*-
"""
@author: Steven Masfaraud
"""

from setuptools import setup
import re

def readme():
    with open('README.rst') as f:
        return f.read()

with open('dessia_api_client/__init__.py','r') as f:
    metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", f.read()))

#print(metadata)

#import powertransmission
setup(name='dessia_api_client',
      version=metadata['version'],
      description="Python client to interact easily with DessIA API",
      long_description='',
      keywords='',
      url='',
      author='Steven Masfaraud',
      author_email='masfaraud@dessia.tech',
      packages=['dessia_api_client'],
      install_requires=['PyJWT', 'requests'])

