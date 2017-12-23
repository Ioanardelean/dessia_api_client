#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 14:59:51 2017

@author: steven
"""

from dessia_api_client import Client

client=Client('masfaraud','admin')


#r=client.AddUser('test','admin','Prénom','Nom','root@dessia.tech')
#print(r)
#r=client.AddTransaction(1,2,3.456,False,'test')

#r=client.TransactionDetails(24)
r=client.VerifyEmail('InJvb3RAZGVzc2lhLnRlY2gi.DR_0GQ.AtSO6m3s284s9dAy6FC5yJdnu-kM')
print(r)