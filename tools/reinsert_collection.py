'''
Created on Apr 3, 2013

@author: Fang Jiaguo
'''

from pymongo.connection import Connection
import time
db = Connection('127.0.0.1', 27017)['right-channel']
for r in db['movies'].find():
    db['temp'].insert(r)

db['movies'].remove()

for r in db['temp'].find():
    db['movies'].insert(r)
    time.sleep(0.001)

db['temp'].remove()


# -*- coding: utf-8 -*-
from pyelasticsearch.client import ElasticSearch
conn = ElasticSearch('http://localhost:9200/')
query = {
    "query": {
        "multi_match": {
            "query": "Legend of the Drunken Master",
            "fields": [
                "title",
                "original_title",
                "aka",
                "directors",
                "casts",
                "countries",
                "genres",
                "summary"
            ]
        }
    }
}
result = conn.search(query, index='rightchannel', doc_type='movie', size=10)
print result.get('hits').get('total')
for r in result.get('hits').get('hits'):
    print r.get('_score'), r.get('_source').get('title'), r.get('_source').get('original_title'), r.get('_source').get('aka')
