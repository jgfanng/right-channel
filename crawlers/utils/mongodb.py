'''
Created on Dec 3, 2012

@author: Fang Jiaguo
'''
from pymongo.connection import Connection

connection = Connection()
db = connection['videocabindb']
movie_store_collection = db['movie.store']
movie_unmatched_collection = db['movie.unmatched']
