'''
Created on Dec 3, 2012

@author: Fang Jiaguo
'''
import time
import urllib
import urllib2

def get(url, params=None, retry_count=3, retry_interval=1):
    '''Send a get request'''
    
    if params:
        url += '?' + urllib.urlencode(params)
    while True:
        try:
            return urllib2.urlopen(url)
        except:
            retry_count -= 1
            if retry_count < 0:
                raise
            elif retry_interval > 0:
                time.sleep(retry_interval)
