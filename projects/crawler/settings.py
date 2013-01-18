'''
Created on Jan 13, 2013

@author: Fang Jiaguo
'''
from pymongo.connection import Connection
import json

settings = json.load(open('settings.json', 'r'))
mongodb = Connection(settings['mongo']['host'], settings['mongo']['port'])[settings['mongo']['db']]
collections = {'movies': mongodb['movies']}
