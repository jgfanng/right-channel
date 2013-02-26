'''
Created on Jan 13, 2013

@author: Fang Jiaguo
'''
from pymongo.connection import Connection
import json

settings = json.load(open('settings.json', 'r'))
mongodb = Connection(settings['mongodb']['host'], settings['mongodb']['port'])[settings['mongodb']['db']]
collections = {'movies': mongodb['movies']}
