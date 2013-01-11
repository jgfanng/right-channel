'''
Created on Dec 3, 2012

@author: Fang Jiaguo
'''
from pymongo.connection import Connection

connection = Connection()
db = connection['right-channel']
movie_collection = db['movie']
movie_douban_collection = db['movie.douban']
