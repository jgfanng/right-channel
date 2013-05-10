'''
Created on Jan 13, 2013

@author: Fang Jiaguo
'''
from pyes.es import ES
from pymongo.connection import Connection
import json

settings = json.load(open('settings.json', 'r'))
mongodb = Connection(settings['mongodb']['host'], settings['mongodb']['port'])[settings['mongodb']['db']]
elasticsearch = ES(('http', settings['elasticsearch']['host'], settings['elasticsearch']['port']))
