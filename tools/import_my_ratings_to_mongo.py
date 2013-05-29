'''
Created on May 29, 2013

@author: yapianyu
'''
from bson.objectid import ObjectId
from pymongo.connection import Connection
import datetime

mongodb = Connection('127.0.0.1', 27017)['right-channel']
uid = ObjectId('518ce9df4597b5adead4b61d')
f = open('../resources/docs/my_ratings.txt')
for line in f:
    mid = ObjectId(line.strip().split(',')[0])
    rating = float(line.strip().split(',')[1])
    mongodb['ratings'].update({'user_id': uid, 'movie_id': mid},
                              {'$set': {'rating': rating, 'last_updated': datetime.datetime.utcnow()}},
                              upsert=True)
