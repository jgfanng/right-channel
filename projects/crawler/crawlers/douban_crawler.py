# -*- coding: utf-8 -*-

'''
Created on Nov 26, 2012

@author: Fang Jiaguo
'''
from Queue import Queue
from lxml.html import fromstring
from pymongo.errors import PyMongoError
from sets import Set
from threading import Thread
from urllib2 import HTTPError, URLError
from urlparse import urldefrag
from utils import request
from utils.fuzzy_date_parser import parse_min_date
from utils.limited_caller import LimitedCaller
from utils.log import get_logger
from utils.settings import collections
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
            DoubanCrawler.logger.info('==========Total movies: %s pages: %s============' % (self.__total_movies_crawled, len(self.__crawled_urls)))

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
                # PATCH 1: remove polluted URLs
                urls = Set()
                for link_element in link_elements:
                    urls.add(urldefrag(link_element.attrib['href'])[0])
                if (url_to_crawl + '?start=20&type=T' in urls and url_to_crawl + '?start=40&type=T' in urls and
                    url_to_crawl + '?start=60&type=T' in urls and url_to_crawl + '?start=80&type=T' in urls and
                    url_to_crawl + '?start=100&type=T' in urls and url_to_crawl + '?start=120&type=T' in urls and
                    url_to_crawl + '?start=140&type=T' in urls and url_to_crawl + '?start=160&type=T' in urls and
                    url_to_crawl + '?start=1960&type=T' in urls and url_to_crawl + '?start=1980&type=T' in urls):
                    continue
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
                movie_id = self.__movie_id_queue.get()  # blocks if the queue is empty
                if movie_id == EOC:
                    break

                movie_info = self.__get_movie_info(movie_id)
                collections['movies'].update({'douban_id': movie_id}, {'$set': movie_info}, upsert=True)

                self.__total_movies_crawled += 1
                DoubanCrawler.logger.info('Crawled movie #%s <%s> QMID(%s) QTAG(%s) QM(%s)' % (self.__total_movies_crawled, movie_info.get('title'), self.__movie_id_queue.qsize(), self.__uncrawled_tag_queue.qsize(), self.__uncrawled_movie_queue.qsize()))

            except PyMongoError, e:
                DoubanCrawler.logger.error('Mongodb error <%s> <%s>' % (e, self.__get_movie_api_url(movie_id)))
            except HTTPError, e:
                DoubanCrawler.logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (self.__get_movie_api_url(movie_id), e.code, e.msg))
            except URLError, e:
                DoubanCrawler.logger.error('Failed to reach server <%s> <%s>' % (self.__get_movie_api_url(movie_id), e.reason))
            except Exception, e:
                DoubanCrawler.logger.error('%s <%s>' % (e, self.__get_movie_api_url(movie_id)))

    def __get_movie_info(self, movie_id):
        '''
        Get movie info using douban api.
        '''

        api_url = self.__get_movie_api_url(movie_id)
        response = self.__movie_api(api_url.encode('utf-8'), query_strings={'apikey': self.apikey}, retry_interval=self.sleep_time)
        response_text = response.read()

        movie_info = json.loads(response_text)
        new_movie_info = {'douban_id': movie_id}
        if 'attrs' in movie_info and 'year' in movie_info['attrs'] and movie_info['attrs']['year'] and movie_info['attrs']['year'][0]:
            new_movie_info['year'] = movie_info['attrs']['year'][0].strip()  # Caution: may not be provided
        if 'title' in movie_info and movie_info['title']:
            new_movie_info['title'] = movie_info['title'].strip()
        if 'alt_title' in movie_info and movie_info['alt_title']:
            new_movie_info['alt_title'] = [item.strip() for item in movie_info['alt_title'].split(' / ') if item.strip()]
        if 'attrs' in movie_info and 'director' in movie_info['attrs'] and movie_info['attrs']['director']:
            new_movie_info['director'] = movie_info['attrs']['director']
        if 'attrs' in movie_info and 'writer' in movie_info['attrs'] and movie_info['attrs']['writer']:
            new_movie_info['writer'] = movie_info['attrs']['writer']
        if 'attrs' in movie_info and 'cast' in movie_info['attrs'] and movie_info['attrs']['cast']:
            new_movie_info['cast'] = movie_info['attrs']['cast']
        if 'attrs' in movie_info and 'episodes' in movie_info['attrs'] and movie_info['attrs']['episodes'] and movie_info['attrs']['episodes'][0]:
            new_movie_info['episodes'] = movie_info['attrs']['episodes'][0]  # Caution: may not be an integer
        if 'attrs' in movie_info and 'movie_type' in movie_info['attrs'] and movie_info['attrs']['movie_type']:
            new_movie_info['type'] = movie_info['attrs']['movie_type']
        if 'attrs' in movie_info and 'country' in movie_info['attrs'] and movie_info['attrs']['country']:
            new_movie_info['country'] = movie_info['attrs']['country']
        if 'attrs' in movie_info and 'language' in movie_info['attrs'] and movie_info['attrs']['language']:
            new_movie_info['language'] = movie_info['attrs']['language']
        if 'attrs' in movie_info and 'pubdate' in movie_info['attrs'] and movie_info['attrs']['pubdate']:
            new_movie_info['pubdate'] = movie_info['attrs']['pubdate']
            min_pubdate = parse_min_date(new_movie_info['pubdate'])
            if min_pubdate:
                new_movie_info['_pubdate'] = parse_min_date(new_movie_info['pubdate'])
        if 'attrs' in movie_info and 'movie_duration' in movie_info['attrs'] and movie_info['attrs']['movie_duration']:
            new_movie_info['duration'] = movie_info['attrs']['movie_duration']
        if 'image' in movie_info and movie_info['image']:
            new_movie_info['image'] = movie_info['image']
        if 'summary' in movie_info and movie_info['summary']:
            new_movie_info['summary'] = movie_info['summary']
        if 'rating' in movie_info and 'average' in movie_info['rating'] and movie_info['rating']['average']:
            new_movie_info['douban_rating'] = float(movie_info['rating']['average'])

        return new_movie_info

    def __get_movie_api_url(self, movie_id):
        '''
        Construct URL to call movie api from movie id.
        '''

        return 'https://api.douban.com/v2/movie/%s' % movie_id

    def __get_movie_page_url(self, movie_id):
        '''
        Construct movie page URL.
        '''

        return 'http://movie.douban.com/subject/%s/' % movie_id
