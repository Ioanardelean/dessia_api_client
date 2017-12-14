#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 14:59:51 2017

@author: steven
"""

from dessia_api_client import Client

client=Client('username','password')

r=client.AddTransaction(1,2,30,'test')
print(r)

r.cli