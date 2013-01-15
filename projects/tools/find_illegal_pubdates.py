# -*- coding: utf-8 -*-
from pymongo.connection import Connection
import re

conn = Connection()
db = conn['right-channel']
coll = db['movies']
regexes = [
    re.compile('(?P<year>\d{4})[-./ ]+(?P<month>\d{1,2})[-./ ]+(?P<day>\d{1,2})'),
    re.compile('(?P<year>\d{4})[-./ ]+(?P<month>\d{1,2})'),
    re.compile('(?P<year>\d{4})年(?P<month>\d{1,2})月(?P<day>\d{1,2})[日号]'),
    re.compile('(?P<year>\d{4})年(?P<month>\d{1,2})月'),
    re.compile('(?P<year>\d{4})')
    ]
index = 1
for movie in coll.find():
    if 'pubdate' in movie:
        for pubdate in movie['pubdate']:
            if isinstance(pubdate, unicode):
                pubdate = pubdate.encode('utf-8')
            good_format = False
            for regex in regexes:
                r = regex.search(pubdate)
                if r:
                    good_format = True
                    break;
            if not good_format:
                print index, pubdate
                index += 1
