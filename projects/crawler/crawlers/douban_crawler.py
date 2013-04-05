# -*- coding: utf-8 -*-

'''
Created on Nov 26, 2012

@author: Fang Jiaguo
'''
from Queue import Queue
from lxml import etree
from lxml.html import fromstring
from pymongo.errors import PyMongoError
from sets import Set
from settings import settings, mongodb
from urllib2 import HTTPError, URLError
from urlparse import urldefrag
from utilities import LimitedCaller, request, get_logger
import datetime
import gzip
import json
import logging
import os
import re
import threading

douban_logger = get_logger('DoubanCrawler', 'douban_crawler.log')
tag_regex = re.compile(settings['douban_crawler']['tag_regex'])
movie_regex = re.compile(settings['douban_crawler']['movie_regex'])
request_douban_api = LimitedCaller(request.get, settings['douban_crawler']['reqs_per_min'])
request_douban_page = LimitedCaller(request.get, settings['douban_crawler']['reqs_per_min'])
tag_url_pool = Queue()
movie_url_pool = Queue()
crawled_url_pool = Set()
low_movie_id_pool = Queue()  # low priority
movie_id_highp_pool = Queue()  # high priority
# in_theaters_movie_ids = Queue()
# coming_soon_movie_ids = Queue()
# top250_movie_ids = Queue()

class DoubanCrawler():
    '''
    Crawler for douban move site (http://movie.douban.com/).
    '''

    def start(self):
        threads = [
            InitialCrawler(),
            LowPriMovieFetcher(),
#            InTheatersCrawler(),
#            InTheatersMovieFetcher(),
#            ComingSoonCrawler(),
#            ComingSoonMovieFetcher(),
#            Top250Crawler(),
#            Top250MovieFetcher()
        ]
        for thread in threads:
            thread.start()

class InitialCrawler(threading.Thread):
    logger = logging.getLogger('DoubanCrawler.InitialCrawler')

    def prepare_seeds(self):
        crawled_url_pool.clear()

        InitialCrawler.logger.info('prepare seeds from config')
        for seed in settings['douban_crawler']['initial_crawler']['seeds']:
            tag_url_pool.put(seed)
            crawled_url_pool.add(seed)

        InitialCrawler.logger.info('prepare seeds from sitemap')
        for sitemap in settings['douban_crawler']['initial_crawler']['sitemaps']:
            sitemap_id = -1
            while True:
                try:
                    sitemap_id += 1
                    xml_name = sitemap % (sitemap_id if sitemap_id else '')
                    zip_name = xml_name + '.gz'
                    xml_path = os.path.join('data', xml_name)
                    zip_path = os.path.join('data', zip_name)
                    zip_url = 'http://www.douban.com/%s' % zip_name
                    # download
                    response = request_douban_page(zip_url)
                    with open(zip_path, 'wb') as out:
                        while True:
                            data = response.read(1024)
                            if len(data) == 0:
                                break
                            out.write(data)
                    InitialCrawler.logger.info('Downloaded <%s>' % zip_name)
                    # extract
                    zip_file = gzip.open(zip_path)
                    with open(xml_path, 'w') as out:
                        for line in zip_file:
                            out.write(line)
                    InitialCrawler.logger.info('Extracted <%s>' % xml_name)
                    # filter movie urls
                    for _, element in etree.iterparse(xml_path, tag='{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                        match = movie_regex.match(element.text)
                        if match:
                            movie_url_pool.put(element.text)
                            crawled_url_pool.add(element.text)
                            low_movie_id_pool.put(match.groupdict().get('id'))

                        # It's safe to call clear() here because no descendants will be accessed
                        element.clear()
                        # Also eliminate now-empty references from the root node to <Title>
                        while element.getprevious() is not None:
                            del element.getparent()[0]

                    os.remove(xml_path)
                    os.remove(zip_path)

                except HTTPError, e:
                    InitialCrawler.logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (zip_url, e.code, e.msg))
                    if e.code == 404:  # no more sitemap found
                        break
                except URLError, e:
                    InitialCrawler.logger.error('Failed to reach server <%s> <%s>' % (zip_url, e.reason))
                except Exception, e:
                    InitialCrawler.logger.error('%s <%s>' % (e, zip_url))

    def run(self):
        while True:  # infinite loop
            InitialCrawler.logger.info('==========InitialCrawler Start==========')

            self.prepare_seeds()
            while True:
                try:
                    if not tag_url_pool.empty():
                        url_to_crawl = tag_url_pool.get()
                    elif not movie_url_pool.empty():
                        url_to_crawl = movie_url_pool.get()
                    else:
                        break

                    response = request_douban_page(url_to_crawl.encode('utf-8'))
                    response_text = response.read()
                    InitialCrawler.logger.debug('Crawled <%s>' % url_to_crawl)

                    html_element = fromstring(response_text)
                    html_element.make_links_absolute(url_to_crawl)
                    link_elements = html_element.xpath('//a[@href]')
                    for link_element in link_elements:
                        url_in_page = urldefrag(link_element.attrib['href'])[0]  # remove fragment identifier
                        if url_in_page not in crawled_url_pool:
                            if tag_regex.match(url_in_page):
                                tag_url_pool.put(url_in_page)
                                crawled_url_pool.add(url_in_page)
                            else:
                                match = movie_regex.match(url_in_page)
                                if match:
                                    movie_url_pool.put(url_in_page)
                                    crawled_url_pool.add(url_in_page)
                                    low_movie_id_pool.put(match.groupdict().get('id'))

                except HTTPError, e:
                    InitialCrawler.logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (url_to_crawl, e.code, e.msg))
                except URLError, e:
                    InitialCrawler.logger.error('Failed to reach server <%s> <%s>' % (url_to_crawl, e.reason))
                except Exception, e:
                    InitialCrawler.logger.error('%s <%s>' % (e, url_to_crawl))

            InitialCrawler.logger.info('==========InitialCrawler Finish==========')

class LowPriMovieFetcher(threading.Thread):
    logger = logging.getLogger('DoubanCrawler.CommonMovieFetcher')

    def run(self):
        while True:  # infinite loop
            try:
                movie_id = low_movie_id_pool.get()  # blocks if the queue is empty
                movie_info = get_movie_info(movie_id)
                subtype = movie_info.pop('subtype')
                if subtype == 'movie':
                    mongodb['movies'].update({'douban.id': movie_id}, {'$set': movie_info}, upsert=True)
                    LowPriMovieFetcher.logger.info('Crawled movie <%s>' % movie_info.get('title'))
                else:
                    mongodb['tv'].update({'douban.id': movie_id}, {'$set': movie_info}, upsert=True)
                    LowPriMovieFetcher.logger.info('Crawled tv <%s>' % movie_info.get('title'))

            except PyMongoError, e:
                LowPriMovieFetcher.logger.error('Mongodb error <%s>' % e)
            except HTTPError, e:
                LowPriMovieFetcher.logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (construct_movie_api_url(movie_id), e.code, e.msg))
            except URLError, e:
                LowPriMovieFetcher.logger.error('Failed to reach server <%s> <%s>' % (construct_movie_api_url(movie_id), e.reason))
            except Exception, e:
                LowPriMovieFetcher.logger.error('%s <%s>' % (e, construct_movie_api_url(movie_id)))

# class InTheatersCrawler(threading.Thread):
#    def run(self):
#        logger = logging.getLogger('DoubanCrawler.InTheatersCrawler')
#        crawled_urls = Set()
#        while True:
#            logger.info('==========InTheatersCrawler Started==========')
#            crawled_urls.clear()  # !important
#
#            try:
#                page = settings['douban_crawler']['in_theaters_crawler']['page']
#                response = request_douban_page(page.encode('utf-8'))
#                response_text = response.read()
#                logger.debug('Crawled <%s>' % page)
#
#                mongodb['movies.collections'].update({'id': 'in_theaters'}, {'$set': {'douban_ids': []}}, upsert=True)  # !important clear douban_ids
#
#                html_element = fromstring(response_text)
#                html_element.make_links_absolute(page)
#                link_elements = html_element.xpath('//a[@href]')
#                for link_element in link_elements:
#                    url_in_page = urldefrag(link_element.attrib['href'])[0]  # remove fragment identifier
#                    if url_in_page not in crawled_urls and movie_regex.match(url_in_page):
#                        crawled_urls.add(url_in_page)
#                        movie_id = url_in_page[len('http://movie.douban.com/subject/'):].replace('/', '')
#                        in_theaters_movie_ids.put(movie_id)
#
#            except PyMongoError, e:
#                logger.error('Mongodb error <%s>' % e)
#            except HTTPError, e:
#                logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (page, e.code, e.msg))
#            except URLError, e:
#                logger.error('Failed to reach server <%s> <%s>' % (page, e.reason))
#            except Exception, e:
#                logger.error('%s <%s>' % (e, page))
#
#            logger.info('==========InTheatersCrawler Finished=========')
#
#            # sleep till next run
#            hour, minute = tuple(settings['douban_crawler']['in_theaters_crawler']['run_at'].split(':'))
#            now = datetime.datetime.utcnow()
#            next_run = datetime.datetime(now.year, now.month, now.day, int(hour), int(minute), now.second) + datetime.timedelta(days=1)  # calculate next run time
#            time.sleep((next_run - now).total_seconds())

# class InTheatersMovieFetcher(threading.Thread):
#    def run(self):
#        logger = logging.getLogger('DoubanCrawler.InTheatersMovieFetcher')
#        while True:
#            try:
#                movie_id = in_theaters_movie_ids.get()  # blocks if the queue is empty
#                movie_info = get_movie_info(movie_id)
#                mongodb['movies'].update({'douban.id': movie_id}, {'$set': movie_info}, upsert=True)
#                mongodb['movies.collections'].update({'id': 'in_theaters'}, {'$push': {'douban_ids': movie_id}}, upsert=True)
#                logger.info('Crawled movie <%s>' % movie_info.get('title'))
#
#            except PyMongoError, e:
#                logger.error('Mongodb error <%s>' % e)
#            except HTTPError, e:
#                logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (construct_movie_api_url(movie_id), e.code, e.msg))
#            except URLError, e:
#                logger.error('Failed to reach server <%s> <%s>' % (construct_movie_api_url(movie_id), e.reason))
#            except Exception, e:
#                logger.error('%s <%s>' % (e, construct_movie_api_url(movie_id)))

# class ComingSoonCrawler(threading.Thread):
#    def run(self):
#        logger = logging.getLogger('DoubanCrawler.ComingSoonCrawler')
#        crawled_urls = Set()
#        while True:
#            logger.info('==========ComingSoonCrawler Started==========')
#            crawled_urls.clear()  # !important
#
#            try:
#                page = settings['douban_crawler']['coming_soon_crawler']['page']
#                response = request_douban_page(page.encode('utf-8'))
#                response_text = response.read()
#                logger.debug('Crawled <%s>' % page)
#
#                mongodb['movies.collections'].update({'id': 'coming_soon'}, {'$set': {'douban_ids': []}}, upsert=True)  # !important clear douban_ids
#
#                html_element = fromstring(response_text)
#                html_element.make_links_absolute(page)
#                link_elements = html_element.xpath('//a[@href]')
#                for link_element in link_elements:
#                    url_in_page = urldefrag(link_element.attrib['href'])[0]  # remove fragment identifier
#                    if url_in_page not in crawled_urls and movie_regex.match(url_in_page):
#                        crawled_urls.add(url_in_page)
#                        movie_id = url_in_page[len('http://movie.douban.com/subject/'):].replace('/', '')
#                        coming_soon_movie_ids.put(movie_id)
#
#            except PyMongoError, e:
#                logger.error('Mongodb error <%s>' % e)
#            except HTTPError, e:
#                logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (page, e.code, e.msg))
#            except URLError, e:
#                logger.error('Failed to reach server <%s> <%s>' % (page, e.reason))
#            except Exception, e:
#                logger.error('%s <%s>' % (e, page))
#
#            logger.info('==========ComingSoonCrawler Finished=========')
#
#            # sleep till next run
#            hour, minute = tuple(settings['douban_crawler']['coming_soon_crawler']['run_at'].split(':'))
#            now = datetime.datetime.utcnow()
#            next_run = datetime.datetime(now.year, now.month, now.day, int(hour), int(minute), now.second) + datetime.timedelta(days=1)  # calculate next run time
#            time.sleep((next_run - now).total_seconds())

# class ComingSoonMovieFetcher(threading.Thread):
#    def run(self):
#        logger = logging.getLogger('DoubanCrawler.ComingSoonMovieFetcher')
#        while True:
#            try:
#                movie_id = coming_soon_movie_ids.get()  # blocks if the queue is empty
#                movie_info = get_movie_info(movie_id)
#                mongodb['movies'].update({'douban.id': movie_id}, {'$set': movie_info}, upsert=True)
#                mongodb['movies.collections'].update({'id': 'coming_soon'}, {'$push': {'douban_ids': movie_id}}, upsert=True)
#                logger.info('Crawled movie <%s>' % movie_info.get('title'))
#
#            except PyMongoError, e:
#                logger.error('Mongodb error <%s>' % e)
#            except HTTPError, e:
#                logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (construct_movie_api_url(movie_id), e.code, e.msg))
#            except URLError, e:
#                logger.error('Failed to reach server <%s> <%s>' % (construct_movie_api_url(movie_id), e.reason))
#            except Exception, e:
#                logger.error('%s <%s>' % (e, construct_movie_api_url(movie_id)))

# class Top250Crawler(threading.Thread):
#    def run(self):
#        logger = logging.getLogger('DoubanCrawler.Top250Crawler')
#        crawled_urls = Set()
#        while True:
#            logger.info('==========Top250Crawler Started==========')
#            crawled_urls.clear()  # !important
#
#            try:
#                page = settings['douban_crawler']['top250_crawler']['page']
#                response = request_douban_page(page.encode('utf-8'))
#                response_text = response.read()
#                logger.debug('Crawled <%s>' % page)
#
#                mongodb['movies.collections'].update({'id': 'top250'}, {'$set': {'douban_ids': []}}, upsert=True)  # !important clear douban_ids
#
#                html_element = fromstring(response_text)
#                html_element.make_links_absolute(page)
#                link_elements = html_element.xpath('//a[@href]')
#                for link_element in link_elements:
#                    url_in_page = urldefrag(link_element.attrib['href'])[0]  # remove fragment identifier
#                    if url_in_page not in crawled_urls and movie_regex.match(url_in_page):
#                        crawled_urls.add(url_in_page)
#                        movie_id = url_in_page[len('http://movie.douban.com/subject/'):].replace('/', '')
#                        top250_movie_ids.put(movie_id)
#
#            except PyMongoError, e:
#                logger.error('Mongodb error <%s>' % e)
#            except HTTPError, e:
#                logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (page, e.code, e.msg))
#            except URLError, e:
#                logger.error('Failed to reach server <%s> <%s>' % (page, e.reason))
#            except Exception, e:
#                logger.error('%s <%s>' % (e, page))
#
#            logger.info('==========Top250Crawler Finished=========')
#
#            # sleep till next run
#            hour, minute = tuple(settings['douban_crawler']['top250_crawler']['run_at'].split(':'))
#            now = datetime.datetime.utcnow()
#            next_run = datetime.datetime(now.year, now.month, now.day, int(hour), int(minute), now.second) + datetime.timedelta(days=1)  # calculate next run time
#            time.sleep((next_run - now).total_seconds())

# class Top250MovieFetcher(threading.Thread):
#    def run(self):
#        logger = logging.getLogger('DoubanCrawler.Top250MovieFetcher')
#        while True:
#            try:
#                movie_id = top250_movie_ids.get()  # blocks if the queue is empty
#                movie_info = get_movie_info(movie_id)
#                mongodb['movies'].update({'douban.id': movie_id}, {'$set': movie_info}, upsert=True)
#                mongodb['movies.collections'].update({'id': 'top250'}, {'$push': {'douban_ids': movie_id}}, upsert=True)
#                logger.info('Crawled movie <%s>' % movie_info.get('title'))
#
#            except PyMongoError, e:
#                logger.error('Mongodb error <%s>' % e)
#            except HTTPError, e:
#                logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (construct_movie_api_url(movie_id), e.code, e.msg))
#            except URLError, e:
#                logger.error('Failed to reach server <%s> <%s>' % (construct_movie_api_url(movie_id), e.reason))
#            except Exception, e:
#                logger.error('%s <%s>' % (e, construct_movie_api_url(movie_id)))

def get_movie_info(movie_id):
    '''
    Get movie info using douban api.
    '''

    api_url = construct_movie_api_url(movie_id)
    response = request_douban_api(api_url.encode('utf-8'), query_strings={'apikey': settings['douban_crawler']['api_key']})
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

    if movie_info.get('alt') and movie_info.get('alt').strip():
        new_movie_info['douban']['url'] = movie_info.get('alt').strip()

    if 'reviews_count' in movie_info:
        new_movie_info['douban']['reviews_count'] = movie_info.get('reviews_count')

    if 'wish_count' in movie_info:
        new_movie_info['douban']['wish_count'] = movie_info.get('wish_count')

    if 'collect_count' in movie_info:
        new_movie_info['douban']['collect_count'] = movie_info.get('collect_count')

    if 'do_count' in movie_info:
        new_movie_info['douban']['do_count'] = movie_info.get('do_count')

    if 'comments_count' in movie_info:
        new_movie_info['douban']['comments_count'] = movie_info.get('comments_count')

    if 'ratings_count' in movie_info:
        new_movie_info['douban']['ratings_count'] = movie_info.get('ratings_count')

    if movie_info.get('subtype'):
        new_movie_info['subtype'] = movie_info.get('subtype')

    return new_movie_info

def construct_movie_url(movie_id):
    '''
    Construct movie URL.
    '''

    return 'http://movie.douban.com/subject/%s/' % movie_id

def construct_movie_api_url(movie_id):
    '''
    Construct URL to call movie api from movie id.
    '''

    return 'https://api.douban.com/v2/movie/subject/%s' % movie_id
