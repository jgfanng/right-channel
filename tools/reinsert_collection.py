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
