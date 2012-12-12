'''
Created on Dec 3, 2012

@author: Fang Jiaguo
'''
from pymongo.connection import Connection

connection = Connection()
db = connection['videocabindb']
movies_unmatched_collection = db['movies.unmatched']
movies_store_collection = db['movies.store']