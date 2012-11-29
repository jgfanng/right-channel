'''
Created on Nov 29, 2012

@author: Fang Jiaguo
'''
from sets import Set
import md5
import urllib2

class WebCrawler:
    '''
    Base crawler
    '''

    def __init__(self, start_urls=None, allowed_domains=None, depth=0):
        self.__start_urls = start_urls
        self.__allowed_domains = allowed_domains
        self.__depth = depth

    def start_crawl(self):
        to_crawl_urls = []
        # push all start urls into "to crawl" list
        for start_url in self.__start_urls:
            to_crawl_urls.append(start_url)

        crawled_urls = Set()
        for to_crawl_url in to_crawl_urls:
            # calculate md5 of the to crawl url
            url_md5 = md5.new(to_crawl_url).digest()
            # filter duplicated urls
            if url_md5 not in crawled_urls:
                crawled_urls.add(md5.new(to_crawl_url).digest())
                request = urllib2.urlopen(to_crawl_url)
                response_text = request.read().decode('utf-8', 'ignore')
                self.__parse(response_text)

    def __parse(self, response_text):
        pass
