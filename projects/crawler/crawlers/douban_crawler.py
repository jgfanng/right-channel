# -*- coding: utf-8 -*-

'''
Created on Nov 26, 2012

@author: Fang Jiaguo
'''
from Queue import Queue
from lxml.html import fromstring
from pymongo.errors import PyMongoError
from sets import Set
from settings import collections, settings
from threading import Thread
from urllib2 import HTTPError, URLError
from urlparse import urldefrag
from util import LimitedCaller
from utils import request
from utils.log import get_logger
import json
import md5
import re

# # douban tag url regular expression
# TAG_URL_RE = re.compile('^http://movie\.douban\.com/tag/[^?]*(\?start=[0-9]+&type=T)?$')
# # douban movie url regular expression
# MOVIE_URL_RE = re.compile('^http://movie\.douban\.com/subject/[0-9]+/?$')
# a special marker to indicate reaching the end of crawling
EOC = 'EndOfCrawl'

class DoubanCrawler():
    '''
    Crawler for douban move site (http://movie.douban.com/).
    '''

    logger = get_logger('DoubanCrawler', 'douban_crawler.log')

    def __init__(self, start_urls):
        # A list of URLs where the crawler will begin to crawl from.
        self.start_urls = start_urls
#        # a queue of URLs to crawl
#        self.__uncrawled_tag_queue = Queue()
#        self.__uncrawled_movie_queue = Queue()
#        # URLs crawled
#        self.crawled_urls = Set()
#        # movie id queue
#        self.movie_id_queue = Queue()
#        # total movies crawled
#        self.__total_movies_crawled = 0
        # Throttle douban api call to 40/60s.
        self.request_movie_api = LimitedCaller(request.get, 60, settings['douban_crawler']['req_per_min'])
        # Throttle douban page crawl to 40/60s.
        self.request_douban_page = LimitedCaller(request.get, 60, settings['douban_crawler']['req_per_min'])

    def start(self):
        while True:
            DoubanCrawler.logger.info('==========Start to crawl douban movies==========')
            self.__start_crawl()
            DoubanCrawler.logger.info('==========Finish crawling douban movies=========')
            DoubanCrawler.logger.info('==========Total movies: %s pages: %s============' % (self.__total_movies_crawled, len(self.crawled_urls)))

    def __start_crawl(self):
        # initialize
        self.crawled_urls.clear()
        self.__total_movies_crawled = 0

        for start_url in self.start_urls:
            url_md5 = md5.new(start_url.encode('utf-8')).digest()
            if url_md5 not in self.crawled_urls:
                self.crawled_urls.add(url_md5)
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
                    self.movie_id_queue.put(EOC)
                    break
                response = self.request_douban_page(url_to_crawl.encode('utf-8'))
                response_text = response.read()
                DoubanCrawler.logger.debug('Crawled <%s>' % url_to_crawl)

                html_element = fromstring(response_text)
                html_element.make_links_absolute(url_to_crawl)
                link_elements = html_element.xpath('//a[@href]')
#                # PATCH 1: remove polluted URLs
#                urls = Set()
#                for link_element in link_elements:
#                    urls.add(urldefrag(link_element.attrib['href'])[0])
#                if (url_to_crawl + '?start=20&type=T' in urls and url_to_crawl + '?start=40&type=T' in urls and
#                    url_to_crawl + '?start=60&type=T' in urls and url_to_crawl + '?start=80&type=T' in urls and
#                    url_to_crawl + '?start=100&type=T' in urls and url_to_crawl + '?start=120&type=T' in urls and
#                    url_to_crawl + '?start=140&type=T' in urls and url_to_crawl + '?start=160&type=T' in urls and
#                    url_to_crawl + '?start=1960&type=T' in urls and url_to_crawl + '?start=1980&type=T' in urls):
#                    continue
                for link_element in link_elements:
                    # remove fragment identifier
                    url_in_page = urldefrag(link_element.attrib['href'])[0]
                    # Add URL if its domain is allowed, and has not been crawled.
                    if TAG_URL_RE.match(url_in_page):
                        url_md5 = md5.new(url_in_page.encode('utf-8')).digest()
                        if url_md5 not in self.crawled_urls:
                            self.crawled_urls.add(url_md5)
                            self.__uncrawled_tag_queue.put(url_in_page)
                    elif MOVIE_URL_RE.match(url_in_page):
                        url_md5 = md5.new(url_in_page.encode('utf-8')).digest()
                        if url_md5 not in self.crawled_urls:
                            self.crawled_urls.add(url_md5)
                            self.__uncrawled_movie_queue.put(url_in_page)
                            movie_id = url_in_page[len('http://movie.douban.com/subject/'):].replace('/', '')
                            self.movie_id_queue.put(movie_id)

            except HTTPError, e:
                DoubanCrawler.logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (url_to_crawl, e.code, e.msg))
            except URLError, e:
                DoubanCrawler.logger.error('Failed to reach server <%s> <%s>' % (url_to_crawl, e.reason))
            except Exception, e:
                DoubanCrawler.logger.error('%s <%s>' % (e, url_to_crawl))

    def __fetch_movies(self):
        '''
        Get movie info using douban api and store it in Mongodb.
        '''

        while True:
            try:
                movie_id = self.movie_id_queue.get()  # blocks if the queue is empty
                if movie_id == EOC:
                    break

                movie_info = self.get_movie_info(movie_id)
                collections['movies'].update({'douban.id': movie_id}, {'$set': movie_info}, upsert=True)

                self.__total_movies_crawled += 1
                DoubanCrawler.logger.info('Crawled movie #%s <%s> QMID(%s) QTAG(%s) QM(%s)' % (self.__total_movies_crawled, movie_info.get('title'), self.movie_id_queue.qsize(), self.__uncrawled_tag_queue.qsize(), self.__uncrawled_movie_queue.qsize()))

            except PyMongoError, e:
                DoubanCrawler.logger.error('Mongodb error <%s> <%s>' % (e, self.make_movie_api_url(movie_id)))
            except HTTPError, e:
                DoubanCrawler.logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (self.make_movie_api_url(movie_id), e.code, e.msg))
            except URLError, e:
                DoubanCrawler.logger.error('Failed to reach server <%s> <%s>' % (self.make_movie_api_url(movie_id), e.reason))
            except Exception, e:
                DoubanCrawler.logger.error('%s <%s>' % (e, self.make_movie_api_url(movie_id)))

    def get_movie_info(self, movie_id):
        '''
        Get movie info using douban api.
        '''

        api_url = self.make_movie_api_url(movie_id)
        response = self.__request_movie_api(api_url.encode('utf-8'), query_strings={'apikey': self.apikey})
        response_text = response.read()

        movie_info = json.loads(response_text)
        new_movie_info = {
            'douban': {
                'id': movie_id
            }
        }

        if movie_info.get('year') and movie_info.get('year').strip():
            new_movie_info['year'] = movie_info.get('year').strip()

        if movie_info.get('title') and movie_info.get('title').strip():
            new_movie_info['title'] = movie_info.get('title').strip()

        if movie_info.get('original_title') and movie_info.get('original_title').strip():
            new_movie_info['original_title'] = movie_info.get('original_title').strip()

        if movie_info.get('aka'):
            new_movie_info['aka'] = movie_info.get('aka')

        if movie_info.get('directors'):
            new_movie_info['directors'] = [director.get('name').strip() for director in movie_info.get('directors') if director and director.get('name').strip()]

        if movie_info.get('casts'):
            new_movie_info['casts'] = [cast.get('name').strip() for cast in movie_info.get('casts') if cast and cast.get('name').strip()]

        if movie_info.get('genres'):
            new_movie_info['genres'] = movie_info.get('genres')

        if movie_info.get('countries'):
            new_movie_info['countries'] = movie_info.get('countries')

        if movie_info.get('images'):
            new_movie_info['images'] = movie_info.get('images')

        if movie_info.get('summary') and movie_info.get('summary').strip():
            new_movie_info['summary'] = movie_info.get('summary').strip()

        if movie_info.get('rating') and 'average' in movie_info.get('rating'):  # average may be 0 !important
            new_movie_info['douban']['rating'] = movie_info.get('rating').get('average')

        if 'ratings_count' in movie_info:  # ratings_count may be 0 !important
            new_movie_info['douban']['raters'] = movie_info.get('ratings_count')

        if movie_info.get('alt') and movie_info.get('alt').strip():
            new_movie_info['douban']['link'] = movie_info.get('alt').strip()

        return new_movie_info

    def make_movie_api_url(self, movie_id):
        '''
        Construct URL to call movie api from movie id.
        '''

        return 'https://api.douban.com/v2/movie/subject/%s' % movie_id
