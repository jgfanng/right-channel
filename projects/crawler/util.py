# -*- coding: utf-8 -*-
'''
Created on Jan 18, 2013

@author: Fang Jiaguo
'''
import calendar
import datetime
import re
import unicodedata

def ispunctuation(c):
    '''
    Return true if char is a punctuation, false otherwise.

    General category names are Letter (L), Mark (M), Number (N),
    Punctuation (P), Symbol (S), Separator (Z), and Other (C).
    '''

    return True if unicodedata.category(c).startswith('P') else False

def contains_cn_char(s):
    '''
    Roughly detect whether a unicode string contains Chinese characters. If contains, return True.
    http://stackoverflow.com/questions/1366068/whats-the-complete-range-for-chinese-characters-in-unicode
    '''

    # Must contain Chinese characters, may contain ASCII characters or punctuation, must not contain other languages.
    # 1. ASCII characters for English (c < 128)
    # 2. Chinese characters: (0x4e00 <= c <= 0x9fff)
    # 3. Punctuation
    contains_cn_char = False
    for c in s:
        if 0x4e00 <= ord(c) <= 0x9fff:
            contains_cn_char = True
        elif ord(c) < 128 or ispunctuation(c):
            continue
        else:
            return False

    return contains_cn_char

regexes = [
    re.compile('(?P<year>\d{4})[-./ ]+(?P<month>\d{1,2})[-./ ]+(?P<day>\d{1,2})'),
    re.compile('(?P<year>\d{4})[-./ ]+(?P<month>\d{1,2})'),
    re.compile('(?P<year>\d{4})年(?P<month>\d{1,2})月(?P<day>\d{1,2})[日号]'),
    re.compile('(?P<year>\d{4})年(?P<month>\d{1,2})月'),
    re.compile('(?P<year>\d{4})')
    ]

def last_day_of_month(year, month):
    _, last_day = calendar.monthrange(year, month)
    return last_day

def parse_date(date_string):
    if isinstance(date_string, unicode):
        date_string = date_string.encode('utf-8')
    for regex in regexes:
        r = regex.search(date_string)
        if r:
            # at least we can find 'year' according to the regex
            year = r.groupdict().get('year')
            month = r.groupdict().get('month') or 12
            day = r.groupdict().get('day') or last_day_of_month(int(year), int(month))
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
