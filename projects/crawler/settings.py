'''
Created on Jan 13, 2013

@author: Fang Jiaguo
'''
from pyelasticsearch.client import ElasticSearch
from pymongo.connection import Connection
import json

settings = json.load(open('settings.json', 'r'))
mongodb = Connection(settings['mongodb']['host'], settings['mongodb']['port'])[settings['mongodb']['db']]
elasticsearch = ElasticSearch('http://127.0.0.1:9200')
