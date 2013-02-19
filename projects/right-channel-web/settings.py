'''
Created on Jan 13, 2013

@author: Fang Jiaguo
'''
import asyncmongo
import json
import re

settings = json.load(open('settings.json', 'r'))
mongodb = asyncmongo.Client(
    pool_id=settings['mongo']['asyncmongo_pool_id'],
    host=settings['mongo']['host'],
    port=settings['mongo']['port'],
    dbname=settings['mongo']['db'])
collections = {
    'movies': mongodb.connection('movies'),
    'accounts': mongodb.connection('accounts')
    }
email_regex = re.compile(settings['email_regex'])
