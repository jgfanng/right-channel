# -*- coding: utf-8 -*-
'''
Created on Apr 12, 2013

@author: Fang Jiaguo
'''
from Queue import Queue
from bson.objectid import ObjectId
from lxml import html
from pymongo.errors import PyMongoError
from sets import Set
from settings import settings, elasticsearch, mongodb
from urllib2 import HTTPError, URLError
from urlparse import urlparse, urlunparse
from utilities import LimitedCaller, send_request, get_logger, calc_similarity
import datetime
import re
import threading

movie_pool = Queue()

class IQIYIMovieCrawler(threading.Thread):
    def __init__(self):
        self.logger = get_logger('IQIYIMovieCrawler', 'iqiyi_movie_crawler.log')
        self.movie_regex = re.compile(settings['iqiyi_crawler']['movie_regex'])
        self.vip_movie_regex = re.compile(settings['iqiyi_crawler']['vip_movie_regex'])
        self.request_iqiyi_page = LimitedCaller(send_request, settings['iqiyi_crawler']['reqs_per_min'])
        threading.Thread.__init__(self)

    def run(self):
        self.logger.info('==========IQIYIMovieCrawler Started==========')

        page_index = 0
        crawled_urls = Set()
        while True:
            try:
                page_index += 1
                page = settings['iqiyi_crawler']['movie_crawler']['page'] % page_index
                response = self.request_iqiyi_page(page.encode('utf-8'))
                response_text = response.read()
                self.logger.debug('Crawled %s', page)
                html_element = html.fromstring(response_text)
                link_elements = html_element.xpath('//a[@href]')

                find_movie = False
                for link_element in link_elements:
                    title = link_element.text
                    scheme, netloc, path, _, _, _ = urlparse(link_element.attrib['href'])
                    url = urlunparse((scheme, netloc, path, None, None, None))  # remove query string
                    if title and title.strip() and url not in crawled_urls and (self.movie_regex.match(url) or self.vip_movie_regex.match(url)):
                        find_movie = True
                        crawled_urls.add(url)
                        title = title.strip()
                        try:
                            directors = None; casts = None
                            response = self.request_iqiyi_page(url.encode('utf-8'))  # request playing page to get (countries, directors, casts)
                            response_text = response.read()
                            self.logger.debug('Crawled %s', url)
                            html_element = html.fromstring(response_text)
                            directors_elements = html_element.xpath(u'//*[normalize-space(text())="导演："]')
                            if directors_elements:
                                directors_element = directors_elements[0]
                                directors = [director.strip() for director in (directors_element.xpath('./a/text()') or directors_element.xpath('../a/text()'))]  # special case
                            casts_elements = html_element.xpath(u'//*[normalize-space(text())="主演："]')
                            if casts_elements:
                                casts_element = casts_elements[0]
                                casts = [cast.strip() for cast in (casts_element.xpath('./a[@href and @title]/text()') or casts_element.xpath('../a/text()'))]  # special case
                        except HTTPError, e:
                            self.logger.error('Server cannot fulfill the request %s %s %s', url, e.code, e.msg)
                        except URLError, e:
                            self.logger.error('Failed to reach server %s %s', url, e.reason)
                        except Exception, e:
                            self.logger.error(e)

                        self.logger.info('Crawled %s(title) %s(director) %s(cast)', title, ' '.join(directors) if directors else None, ' '.join(casts) if casts else None)
                        movie_pool.put(('iqiyi', url, title, None, None, directors, casts))

                if not find_movie:
                    page_index = 0
                    crawled_urls.clear()

            except HTTPError, e:
                self.logger.error('Server cannot fulfill the request %s %s %s', page, e.code, e.msg)
            except URLError, e:
                self.logger.error('Failed to reach server %s %s', page, e.reason)
            except Exception, e:
                self.logger.error(e)

        self.logger.info('==========IQIYIMovieCrawler Finished=========')

class OnlineMovieMatcher(threading.Thread):
    def __init__(self):
        self.logger = get_logger('OnlineMovieMatcher', 'online_movie_crawler.log')
        threading.Thread.__init__(self)

    def run(self):
        while True:
            try:
                source, url, title, year, countries, directors, casts = movie_pool.get()
                query = {
                    'query': {
                        'multi_match': {
                            'query': title,
                            'fields': [
                                'title',
                                'original_title',
                                'aka'
                            ]
                        }
                    }
                }
                result = elasticsearch.search(query, index=settings['elasticsearch']['index'], doc_type='movie', size=10)
                max_score = 0
                max_movie = None
                for r in result.get('hits').get('hits'):
                    title_ = r.get('_source').get('title')
                    original_title_ = r.get('_source').get('original_title')
                    aka_ = r.get('_source').get('aka')
                    year_ = r.get('_source').get('year')
                    countries_ = r.get('_source').get('countries')
                    directors_ = r.get('_source').get('directors')
                    casts_ = r.get('_source').get('casts')

                    score = 0
                    if title_:
                        score = max(calc_similarity(title_, title), score)
                    if original_title_:
                        score = max(calc_similarity(original_title_, title), score)
                    if aka_:
                        for t in aka_:
                            score = max(calc_similarity(t, title), score)
                    if year and year_ and year == year_:
                        score += 1
                    if countries and countries_:
                        for country in countries:
                            if country in countries_:
                                score += 1
                    if directors and directors_:
                        for director in directors:
                            if director in directors_:
                                score += 1
                    if casts and casts_:
                        for cast in casts:
                            if cast in casts_:
                                score += 1

                    if score > max_score:
                        max_score = score
                        max_movie = r

                if max_movie:
                    mongodb['movies'].update({'_id': ObjectId(max_movie.get('_source').get('_id'))},
                                             {'$set': {'resources.online.%s' % source: {'url': url, 'similarity': max_score, 'last_updated': datetime.datetime.utcnow()}}})
                    self.logger.info('%s(%s) %s(douban) %s(similarity)', title, source, max_movie.get('_source').get('title'), max_score)
                else:
                    self.logger.warn('No similar movie for %s(%s)', title, source)
            except PyMongoError, e:
                self.logger.error('Mongodb error %s' % e)
            except Exception, e:
                self.logger.error(e)
