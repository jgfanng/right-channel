'''
Created on Jan 13, 2013

@author: Fang Jiaguo
'''
import asyncmongo
import json
import re

settings = json.load(open('settings.json', 'r'))
mongodb = asyncmongo.Client(
    pool_id='pool_id',
    host=settings['mongodb']['host'],
    port=settings['mongodb']['port'],
    dbname=settings['mongodb']['db'])
email_regex = re.compile(settings['email_regex'])
