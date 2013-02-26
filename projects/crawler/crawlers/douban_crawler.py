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
import datetime
import json
import logging
import re
import threading

douban_logger = get_logger('DoubanCrawler', 'douban_crawler.log')
tag_regex = re.compile(settings['douban_crawler']['tag_regex'])
movie_regex = re.compile(settings['douban_crawler']['movie_regex'])
request_movie_api = LimitedCaller(request.get, 60, settings['douban_crawler']['req_per_min'])
request_douban_page = LimitedCaller(request.get, 60, settings['douban_crawler']['req_per_min'])
common_movie_ids = Queue()
in_theater_movie_ids = Queue()

class DoubanCrawler():
    '''
    Crawler for douban move site (http://movie.douban.com/).
    '''

    def start(self):
        seeds_crawler = Thread(target=self.crawl_from_seeds)
        in_theater_crawler = Thread(target=self.crawl_in_theater)
        movie_fetcher = Thread(target=self.fetch_movies)
        seeds_crawler.start()
        in_theater_crawler.start()
        movie_fetcher.start()

class SeedsCrawler(threading.Thread):
    def run(self):
        logger = logging.getLogger('DoubanCrawler.SeedsCrawler')
        tag_urls = Queue()
        movie_urls = Queue()
        crawled_urls = Set()
        while True:
            logger.info('==========SeedsCrawler Started==========')
            for seed in settings['douban_crawler']['seeds_crawler']['seeds']:
                tag_urls.put(seed)
                crawled_urls.add(seed)

            while True:
                try:
                    if not tag_urls.empty():
                        url_to_crawl = tag_urls.get()
                    elif not movie_urls.empty():
                        url_to_crawl = movie_urls.get()
                    else:
                        crawled_urls.clear()  # prepare to start next round
                        break

                    response = request_douban_page(url_to_crawl.encode('utf-8'))
                    response_text = response.read()
                    logger.debug('Crawled <%s>' % url_to_crawl)

                    html_element = fromstring(response_text)
                    html_element.make_links_absolute(url_to_crawl)
                    link_elements = html_element.xpath('//a[@href]')
                    for link_element in link_elements:
                        url_in_page = urldefrag(link_element.attrib['href'])[0]  # remove fragment identifier
                        if url_in_page not in crawled_urls:
                            if tag_regex.match(url_in_page):
                                tag_urls.put(url_in_page)
                                crawled_urls.add(url_in_page)
                            elif movie_regex.match(url_in_page):
                                movie_urls.put(url_in_page)
                                crawled_urls.add(url_in_page)
                                movie_id = url_in_page[len('http://movie.douban.com/subject/'):].replace('/', '')
                                common_movie_ids.put(movie_id)

                except HTTPError, e:
                    logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (url_to_crawl, e.code, e.msg))
                except URLError, e:
                    logger.error('Failed to reach server <%s> <%s>' % (url_to_crawl, e.reason))
                except Exception, e:
                    logger.error('%s <%s>' % (e, url_to_crawl))

            logger.info('==========SeedsCrawler Finished=========')

class InTheaterCrawler(threading.Thread):
    def run(self):
        logger = logging.getLogger('DoubanCrawler.InTheaterCrawler')
        while True:
            logger.info('==========InTheaterCrawler Started==========')

            try:
                page = settings['douban_crawler']['in_theater_crawler']['page']
                response = request_douban_page(page.encode('utf-8'))
                response_text = response.read()
                logger.debug('Crawled <%s>' % page)

                # remove previous records
                collections['movies.in_theater'].remove()

                html_element = fromstring(response_text)
                html_element.make_links_absolute(page)
                link_elements = html_element.xpath('//a[@href]')
                for link_element in link_elements:
                    url_in_page = urldefrag(link_element.attrib['href'])[0]  # remove fragment identifier
                    if movie_regex.match(url_in_page):
                        movie_id = url_in_page[len('http://movie.douban.com/subject/'):].replace('/', '')
                        in_theater_movie_ids.put(movie_id)

            except PyMongoError, e:
                logger.error('Mongodb error <%s>' % e)
            except HTTPError, e:
                logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (page, e.code, e.msg))
            except URLError, e:
                logger.error('Failed to reach server <%s> <%s>' % (page, e.reason))
            except Exception, e:
                logger.error('%s <%s>' % (e, page))

            logger.info('==========InTheaterCrawler Finished=========')

class CommonMovieFetcher(threading.Thread):
    def run(self):
        logger = logging.getLogger('DoubanCrawler.CommonMovieFetcher')
        while True:
            try:
                movie_id = common_movie_ids.get()  # blocks if the queue is empty
                movie_info = get_movie_info(movie_id)
                collections['movies'].update({'douban.id': movie_id}, {'$set': movie_info}, upsert=True)
                logger.info('Crawled movie <%s>' % movie_info.get('title'))

            except PyMongoError, e:
                logger.error('Mongodb error <%s>' % e)
            except HTTPError, e:
                logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (make_movie_api_url(movie_id), e.code, e.msg))
            except URLError, e:
                logger.error('Failed to reach server <%s> <%s>' % (make_movie_api_url(movie_id), e.reason))
            except Exception, e:
                logger.error('%s <%s>' % (e, make_movie_api_url(movie_id)))

class InTheaterMovieFetcher(threading.Thread):
    def run(self):
        logger = logging.getLogger('DoubanCrawler.InTheaterMovieFetcher')
        while True:
            try:
                movie_id = in_theater_movie_ids.get()  # blocks if the queue is empty
                movie_info = get_movie_info(movie_id)
                collections['movies'].update({'douban.id': movie_id}, {'$set': movie_info}, upsert=True)
                collections['movies.in_theater'].insert
                logger.info('Crawled movie <%s>' % movie_info.get('title'))

            except PyMongoError, e:
                logger.error('Mongodb error <%s>' % e)
            except HTTPError, e:
                logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (make_movie_api_url(movie_id), e.code, e.msg))
            except URLError, e:
                logger.error('Failed to reach server <%s> <%s>' % (make_movie_api_url(movie_id), e.reason))
            except Exception, e:
                logger.error('%s <%s>' % (e, make_movie_api_url(movie_id)))

def get_movie_info(movie_id):
    '''
    Get movie info using douban api.
    '''

    api_url = make_movie_api_url(movie_id)
    response = request_movie_api(api_url.encode('utf-8'), query_strings={'apikey': settings['douban_crawler']['api_key']})
    response_text = response.read()

    movie_info = json.loads(response_text)
    new_movie_info = {
        'douban': {
            'id': movie_id,
            'last_updated': datetime.datetime.utcnow()
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

def make_movie_api_url(movie_id):
    '''
    Construct URL to call movie api from movie id.
    '''

    return 'https://api.douban.com/v2/movie/subject/%s' % movie_id
