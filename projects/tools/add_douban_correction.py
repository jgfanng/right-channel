# -*- coding: utf-8 -*-
'''
Created on Dec 25, 2012

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from crawlers.utilities.mongodb import movie_douban_correction_collection

def add_douban_correction(_id, movie_info):
    movie_douban_correction_collection.update({'_id': _id}, {'$set': movie_info}, upsert=True)

add_douban_correction(ObjectId("50d88fd10c468ecda4b78b16"), {'alt_title': '冈格尔的复仇'})
