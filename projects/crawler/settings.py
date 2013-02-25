'''
Created on Jan 13, 2013

@author: Fang Jiaguo
'''
from pymongo.connection import Connection
import json
import re

settings = json.load(open('settings.json', 'r'))
mongodb = Connection(settings['mongodb']['host'], settings['mongodb']['port'])[settings['mongodb']['db']]
collections = {'movies': mongodb['movies']}
tag_regex = re.compile(settings['douban_crawler']['tag_regex'])
movie_regex = re.compile(settings['douban_crawler']['movie_regex'])
