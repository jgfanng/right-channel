'''
Created on Dec 3, 2012

@author: Fang Jiaguo
'''
from pymongo.connection import Connection

connection = Connection()
db = connection['videocabindb']
movie_douban_collection = db['movie.douban']
movie_source_collection = db['movie.source']
