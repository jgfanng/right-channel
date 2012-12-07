'''
Created on Dec 3, 2012

@author: Fang Jiaguo
'''
from urllib import urlencode
from urlparse import urlparse, parse_qs, urlunparse
import time
import urllib2

def get(url, additional_qs=None, retry_interval=5, retry_count=3):
    '''Send a get request'''

    if additional_qs:
        # urlparse returns tuple, then convert tuple to list
        parse_result = list(urlparse(url))
        # parse the 4th element (query string)
        qs = parse_qs(parse_result[4])
        qs.update(additional_qs)
        new_qs = urlencode(qs, doseq=True)
        parse_result[4] = new_qs
        url = urlunparse(parse_result)

    while True:
        try:
            return urllib2.urlopen(url.encode('utf-8'), timeout=30)
        except:
            retry_count -= 1
            if retry_count < 0:
                raise
            elif retry_interval > 0:
                time.sleep(retry_interval)
