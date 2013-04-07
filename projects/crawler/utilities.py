# -*- coding: utf-8 -*-
'''
Created on Jan 18, 2013

@author: Fang Jiaguo
'''
from difflib import SequenceMatcher
from urllib import urlencode
from urlparse import urlparse, parse_qs, urlunparse
import logging.handlers
import os
import threading
import time
import urllib2

class LimitedCaller(object):
    '''
    Limit function call under a threshold in a given period.
    '''

    def __init__(self, method, max_calls, period=60):
        self.__method = method  # the function to call
        self.__max_calls = max_calls  # max calls be made in the given period
        self.__period = period  # in seconds
        self.__call_times = []
        self.__lock = threading.Lock()

    def __call__(self, *args, **kwargs):
        with self.__lock:
            now = time.time()
            times = [t for t in self.__call_times if now - t <= self.__period]
            if len(times) >= self.__max_calls:
                t = times[0] + self.__period - now
                time.sleep(t)
            self.__call_times = times + [time.time()]
        return self.__method(*args, **kwargs)

# def ispunctuation(c):
#    '''
#    Return true if char is a punctuation, false otherwise.
#
#    General category names are Letter (L), Mark (M), Number (N),
#    Punctuation (P), Symbol (S), Separator (Z), and Other (C).
#    '''
#
#    return True if unicodedata.category(c).startswith('P') else False

# def possibly_chinese(s):
#    '''
#    Roughly detect whether a unicode string contains Chinese characters. If contains, return True.
#    http://stackoverflow.com/questions/1366068/whats-the-complete-range-for-chinese-characters-in-unicode
#    '''
#
#    # Must contain Chinese characters, may contain ASCII characters or punctuation, must not contain other languages.
#    # 1. ASCII characters for English (c < 128)
#    # 2. Chinese characters: (0x4e00 <= c <= 0x9fff)
#    # 3. Punctuation
#    possibly_chinese = False
#    for c in s:
#        if 0x4e00 <= ord(c) <= 0x9fff:
#            possibly_chinese = True
#        elif ord(c) < 128 or ispunctuation(c):
#            continue
#        else:
#            return False
#
#    return possibly_chinese

# regexes = [
#    re.compile('(?P<year>\d{4})[-./ ]+(?P<month>\d{1,2})[-./ ]+(?P<day>\d{1,2})'),
#    re.compile('(?P<year>\d{4})[-./ ]+(?P<month>\d{1,2})'),
#    re.compile('(?P<year>\d{4})年(?P<month>\d{1,2})月(?P<day>\d{1,2})[日号]'),
#    re.compile('(?P<year>\d{4})年(?P<month>\d{1,2})月'),
#    re.compile('(?P<year>\d{4})')
#    ]
#
# def last_day_of_month(year, month):
#    _, last_day = calendar.monthrange(year, month)
#    return last_day
#
# def parse_date(date_string):
#    if isinstance(date_string, unicode):
#        date_string = date_string.encode('utf-8')
#    for regex in regexes:
#        r = regex.search(date_string)
#        if r:
#            # at least we can find 'year' according to the regex
#            year = r.groupdict().get('year')
#            month = r.groupdict().get('month') or 12
#            day = r.groupdict().get('day') or last_day_of_month(int(year), int(month))
#            try:
#                return datetime.datetime(int(year), int(month), int(day))
#            except:
#                return None
#    return None
#
# def parse_min_date(date_strings):
#    if not date_strings:
#        return None
#
#    min_date = None
#    for date_string in date_strings:
#        date = parse_date(date_string)
#        if date:
#            if not min_date or date < min_date:
#                min_date = date
#    return min_date

def send_request(url, query_strings=None):
    '''Send a get request'''

    if query_strings:
        # urlparse returns tuple, then convert tuple to list
        parse_result = list(urlparse(url))
        # parse the 4th element (query string)
        qs = parse_qs(parse_result[4])
        qs.update(query_strings)
        new_qs = urlencode(qs, doseq=True)
        parse_result[4] = new_qs
        url = urlunparse(parse_result)

    return urllib2.urlopen(url)

def get_logger(name, log_file):
    # Severity level: DEBUG/INFO/WARN/ERROR/CRITICAL
    logger = logging.getLogger(name)
    # Set to DEBUG when the application is under debugging, otherwise INFO.
    logger.setLevel(logging.DEBUG)
    # Create file handler with INFO log level accepting higher severity level than INFO.
    file_handler = logging.handlers.RotatingFileHandler(os.path.join('logs', log_file), maxBytes=1024 * 1024 * 1024 * 2, backupCount=3)
    file_handler.setLevel(logging.DEBUG)
    # Create console handler with a higher DEBUG level accepting higher severity level than DEBUG.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # Create formatter and add it to the handlers
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    # Add handlers to logger.
    logger.handlers = [file_handler, console_handler]

    return logger

def calc_similarity(s_base, s_another):
    if s_base is None or s_another is None:
        return 0

    m = SequenceMatcher(None, s_base, s_another)
    if len(s_base) >= len(s_another):
        return m.ratio()

    # each block represents a sequence of matching characters in a string
    # of the form (idx_1, idx_2, len)
    # the best partial match will block align with at least one of those blocks
    #   e.g. shorter = "abcd", longer = XXXbcdeEEE
    #   block = (1,3,3)
    #   best score === ratio("abcd", "Xbcd")
    blocks = m.get_matching_blocks()
    scores = []
    for block in blocks:
        start = block[1] - block[0] if (block[1] - block[0]) > 0 else 0
        end = start + len(s_base)
        s_sub = s_another[start:end]

        m = SequenceMatcher(None, s_base, s_sub)
        scores.append(m.ratio())

    return max(scores)
