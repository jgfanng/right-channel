'''
Created on Nov 26, 2012

@author: Fang Jiaguo
'''

class CrawlerBase:
    '''
    Base class for crawler.
    '''

    def __init__(self, sleep_time=60):
        self.__sleep_time = sleep_time

    def crawl(self):
        pass
