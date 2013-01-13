# -*- coding: utf-8 -*-
'''
Created on Jan 13, 2013

@author: Fang Jiaguo
'''
import datetime
import re

regexes = [
    re.compile('(?P<year>\d{4})[-./ ]+(?P<month>\d{1,2})[-./ ]+(?P<day>\d{1,2})'),
    re.compile('(?P<year>\d{4})[-./ ]+(?P<month>\d{1,2})'),
    re.compile('(?P<year>\d{4})年(?P<month>\d{1,2})月(?P<day>\d{1,2})[日号]'),
    re.compile('(?P<year>\d{4})年(?P<month>\d{1,2})月'),
    re.compile('(?P<year>\d{4})')
    ]

def parse_date(date_string):
    for regex in regexes:
        r = regex.search(date_string)
        if r:
            # at least we can find 'year' according to the regexes
            year = r.groupdict().get('year')
            month = r.groupdict().get('month') or 12
            day = r.groupdict().get('day') or 28  # lazy man's method!
            try:
                return datetime.datetime(int(year), int(month), int(day))
            except:
                return None
    return None

def parse_min_date(date_strings):
    if not date_strings:
        return None

    min_date = None
    for date_string in date_strings:
        date = parse_date(date_string)
        if date:
            if not min_date or date < min_date:
                min_date = date
    return min_date
