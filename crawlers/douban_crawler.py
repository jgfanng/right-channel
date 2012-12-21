# -*- coding: utf-8 -*-

'''
Created on Nov 26, 2012

@author: Fang Jiaguo
'''
from Queue import Queue
from crawlers.utils import request
from crawlers.utils.limited_caller import LimitedCaller
from crawlers.utils.log import get_logger
from crawlers.utils.mongodb import movie_douban_collection
from lxml.html import fromstring
from pymongo.errors import PyMongoError
from sets import Set
from threading import Thread
from urllib2 import HTTPError, URLError
from urlparse import urldefrag
import json
import md5
import re
import time

# douban tag url regular expression
TAG_URL_RE = re.compile('^http://movie\.douban\.com/tag/[^?]*(\?start=[0-9]+&type=T)?$')
# douban movie url regular expression
MOVIE_URL_RE = re.compile('^http://movie\.douban\.com/subject/[0-9]+/?$')
# a special marker to indicate reaching the end of crawling
EOC = 'EndOfCrawl'

class DoubanCrawler():
    '''
    Crawler for douban move site (http://movie.douban.com/).
    '''

    logger = get_logger('DoubanCrawler', 'douban_crawler.log')

    def __init__(self, start_urls, apikey, sleep_time=5):
        # A list of URLs where the crawler will begin to crawl from.
        self.start_urls = start_urls
        # apikey carried to call douban api, allowing 40apis/1m.
        self.apikey = apikey
        # sleep time between two crawls for throttle
        self.sleep_time = sleep_time
        # a queue of URLs to crawl
        self.__uncrawled_tag_queue = Queue()
        self.__uncrawled_movie_queue = Queue()
        # md5 of URLs crawled
        self.__crawled_urls = Set()
        # movie id queue
        self.__movie_id_queue = Queue()
        # total movies crawled
        self.__total_movies_crawled = 0
        # Throttle douban api call to 40 apis within 60s.
        self.__movie_api = LimitedCaller(request.get, 60, 40)

    def start_crawl(self):
        while True:
            DoubanCrawler.logger.info('==========Start to crawl douban movies==========')
            self.__start_crawl()
            DoubanCrawler.logger.info('==========Finish crawling douban movies=========')
            DoubanCrawler.logger.info('==========Total movies(%s) pages(%s)============' % (self.__total_movies_crawled, len(self.__crawled_urls)))

    def __start_crawl(self):
        # initialize
        self.__crawled_urls.clear()
        self.__total_movies_crawled = 0

        for start_url in self.start_urls:
            url_md5 = md5.new(start_url.encode('utf-8')).digest()
            if url_md5 not in self.__crawled_urls:
                self.__crawled_urls.add(url_md5)
                self.__uncrawled_tag_queue.put(start_url)

        # create two threads: one to find movie, the other to fetch movie
        movie_finder = Thread(target=self.__find_movies)
        movie_fetcher = Thread(target=self.__fetch_movies)
        movie_finder.start()
        movie_fetcher.start()
        movie_finder.join()
        movie_fetcher.join()

    def __find_movies(self):
        '''
        Crawl douban pages to extract movie URLs.
        '''

        while True:
            try:
                if not self.__uncrawled_tag_queue.empty():
                    url_to_crawl = self.__uncrawled_tag_queue.get()
                elif not self.__uncrawled_movie_queue.empty():
                    url_to_crawl = self.__uncrawled_movie_queue.get()
                else:
                    # push a special marker to indicate reaching the end of crawling
                    self.__movie_id_queue.put(EOC)
                    break
                response = request.get(url_to_crawl.encode('utf-8'), retry_interval=self.sleep_time)
                response_text = response.read()
                DoubanCrawler.logger.debug('Crawled <%s>' % url_to_crawl)
                if self.sleep_time > 0:
                    time.sleep(self.sleep_time)

                html_element = fromstring(response_text)
                html_element.make_links_absolute(url_to_crawl)
                link_elements = html_element.xpath('//a[@href]')
                for link_element in link_elements:
                    # remove fragment identifier
                    url_in_page = urldefrag(link_element.attrib['href'])[0]
                    # Add URL if its domain is allowed, and has not been crawled.
                    if TAG_URL_RE.match(url_in_page):
                        url_md5 = md5.new(url_in_page.encode('utf-8')).digest()
                        if url_md5 not in self.__crawled_urls:
                            self.__crawled_urls.add(url_md5)
                            self.__uncrawled_tag_queue.put(url_in_page)
                    elif MOVIE_URL_RE.match(url_in_page):
                        url_md5 = md5.new(url_in_page.encode('utf-8')).digest()
                        if url_md5 not in self.__crawled_urls:
                            self.__crawled_urls.add(url_md5)
                            self.__uncrawled_movie_queue.put(url_in_page)
                            movie_id = url_in_page[len('http://movie.douban.com/subject/'):].replace('/', '')
                            self.__movie_id_queue.put(movie_id)

            except HTTPError, e:
                DoubanCrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (url_to_crawl, e.code, e.msg))
            except URLError, e:
                DoubanCrawler.logger.error('Failed to reach server <%s %s>' % (url_to_crawl, e.reason))
            except Exception, e:
                DoubanCrawler.logger.error('%s <%s>' % (e, url_to_crawl))

    def __fetch_movies(self):
        '''
        Get movie info using douban api and store it in Mongodb.
        '''

        while True:
            try:
                movie_id = self.__movie_id_queue.get()  # blocks if the queue is empty
                if movie_id == EOC:
                    break
                api_url = self.__get_movie_api_url(movie_id)
                response = self.__movie_api(api_url.encode('utf-8'), query_strings={'apikey': self.apikey}, retry_interval=self.sleep_time)
                response_text = response.read()
                movie_info = json.loads(response_text)
                movie_info['id'] = movie_id  # change default id to movie id
                movie_douban_collection.update({'id': movie_id}, movie_info, upsert=True)

                self.__total_movies_crawled += 1
                DoubanCrawler.logger.info('Crawled movie #%s <%s> QMID(%s) QTAG(%s) QM(%s)' % (self.__total_movies_crawled, movie_info['title'], self.__movie_id_queue.qsize(), self.__uncrawled_tag_queue.qsize(), self.__uncrawled_movie_queue.qsize()))

            except PyMongoError, e:
                DoubanCrawler.logger.error('Mongodb error <%s %s>' % (e, self.__get_movie_api_url(movie_id)))
            except HTTPError, e:
                DoubanCrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (self.__get_movie_api_url(movie_id), e.code, e.msg))
            except URLError, e:
                DoubanCrawler.logger.error('Failed to reach server <%s %s>' % (self.__get_movie_api_url(movie_id), e.reason))
            except Exception, e:
                DoubanCrawler.logger.error('%s <%s>' % (e, self.__get_movie_api_url(movie_id)))

    def __url_is_allowed(self, url):
        '''
        Return True if URL pattern is allowed, otherwise False.
        '''

        if not self.allowed_url_res:
            return True

        for re in self.allowed_url_res:
            if re.match(url):
                return True

        return False

    def __get_movie_api_url(self, movie_id):
        '''
        Construct URL to call movie api from movie id.
        '''

        return 'https://api.douban.com/v2/movie/%s' % movie_id
