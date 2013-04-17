# -*- coding: utf-8 -*-
'''
Created on Apr 12, 2013

@author: Fang Jiaguo
'''
from Queue import Queue
from bson.objectid import ObjectId
from lxml import html
from pymongo.errors import PyMongoError
from settings import settings, elasticsearch, mongodb
from urllib2 import HTTPError, URLError
from utilities import LimitedCaller, send_request, get_logger, calc_similarity
import datetime
import threading

logger = get_logger('OnlineMovieCrawler', 'online_movie_crawler.log')
movie_pool = Queue()

class IQIYIMovieCrawler(threading.Thread):
    def __init__(self):
        self.provider = 'iqiyi'
        self.logger = logger.getChild('IQIYIMovieCrawler')
        self.request_iqiyi_page = LimitedCaller(send_request, settings['online_movie_crawler']['iqiyi_movie_crawler']['reqs_per_min'])
        threading.Thread.__init__(self)

    def run(self):
        page_index = 0
        while True:
            try:
                page_index += 1
                page = settings['online_movie_crawler']['iqiyi_movie_crawler']['page'] % page_index
                response = self.request_iqiyi_page(page)
                response_text = response.read()
                self.logger.debug('Crawled %s', page)
                html_element = html.fromstring(response_text)
                li_elements = html_element.xpath('//ul/li/a[re:match(@href, "%s") and @class="title"]/..' % settings['online_movie_crawler']['iqiyi_movie_crawler']['url_regex'],
                                                 namespaces={'re': 'http://exslt.org/regular-expressions'})

                find_movie = False
                for li_element in li_elements:
                    title_elements = li_element.xpath('./a[re:match(@href, "%s") and @class="title"]' % settings['online_movie_crawler']['iqiyi_movie_crawler']['url_regex'],
                                                  namespaces={'re': 'http://exslt.org/regular-expressions'})
                    if title_elements:
                        find_movie = True
                        url = title_elements[0].attrib['href']
                        title = title_elements[0].text
                        directors = None
                        casts = None
                        directors_elements = li_element.xpath(u'.//*[normalize-space(text())="导演："]/..')
                        if directors_elements:
                            directors = directors_elements[0].xpath('./a/text()')
                        casts_elements = li_element.xpath(u'.//*[normalize-space(text())="主演："]/..')
                        if casts_elements:
                            casts = casts_elements[0].xpath('./a/text()')

                        movie_pool.put(MovieItem(self.provider, url, title, directors=directors, casts=casts))
                        self.logger.info('Crawled %s(title) %s(director) %s(cast)', title, ' '.join(directors) if directors else None, ' '.join(casts) if casts else None)

                if not find_movie:
                    page_index = 0

            except HTTPError, e:
                self.logger.error('Server cannot fulfill the request %s %s %s', page, e.code, e.msg)
            except URLError, e:
                self.logger.error('Failed to reach server %s %s', page, e.reason)
            except Exception, e:
                self.logger.error(e)

        self.logger.info('==========IQIYIMovieCrawler Finished=========')

class PPTVMovieCrawler(threading.Thread):
    def __init__(self):
        self.provider = 'pptv'
        self.logger = logger.getChild('PPTVMovieCrawler')
        self.request_pptv_page = LimitedCaller(send_request, settings['online_movie_crawler']['pptv_movie_crawler']['reqs_per_min'])
        threading.Thread.__init__(self)

    def run(self):
        page_index = 0
        while True:
            try:
                page_index += 1
                page = settings['online_movie_crawler']['pptv_movie_crawler']['page'] % page_index
                response = self.request_pptv_page(page)
                response_text = response.read()
                self.logger.debug('Crawled %s', page)
                html_element = html.fromstring(response_text)
                li_elements = html_element.xpath('//ul/li/p/a[re:match(@href, "%s") and @title]/../..' % settings['online_movie_crawler']['pptv_movie_crawler']['url_regex'],
                                                 namespaces={'re': 'http://exslt.org/regular-expressions'})

                find_movie = False
                for li_element in li_elements:
                    title_elements = li_element.xpath('./p/a[re:match(@href, "%s") and @title]' % settings['online_movie_crawler']['pptv_movie_crawler']['url_regex'],
                                                  namespaces={'re': 'http://exslt.org/regular-expressions'})
                    if title_elements:
                        find_movie = True
                        url = title_elements[0].attrib['href']
                        title = title_elements[0].attrib['title']
                        casts = None
                        casts_elements = li_element.xpath(u'.//*[normalize-space(text())="演员:"]')
                        if casts_elements:
                            casts = casts_elements[0].xpath('./a/@title')

                        movie_pool.put(MovieItem(self.provider, url, title, casts=casts))
                        self.logger.info('Crawled %s(title) %s(cast)', title, ' '.join(casts) if casts else None)

                if not find_movie:
                    page_index = 0

            except HTTPError, e:
                self.logger.error('Server cannot fulfill the request %s %s %s', page, e.code, e.msg)
            except URLError, e:
                self.logger.error('Failed to reach server %s %s', page, e.reason)
            except Exception, e:
                self.logger.error(e)

class OnlineMovieMatcher(threading.Thread):
    def __init__(self):
        self.logger = logger.getChild('OnlineMovieMatcher')
        threading.Thread.__init__(self)

    def run(self):
        while True:
            try:
                movie_item = movie_pool.get()
                query = {
                    'query': {
                        'multi_match': {
                            'query': movie_item.title,
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
                    title = r.get('_source').get('title')
                    original_title = r.get('_source').get('original_title')
                    aka = r.get('_source').get('aka')
                    year = r.get('_source').get('year')
                    countries = r.get('_source').get('countries')
                    directors = r.get('_source').get('directors')
                    casts = r.get('_source').get('casts')

                    score = 0
                    if title:
                        score = max(calc_similarity(title, movie_item.title), score)
                    if original_title:
                        score = max(calc_similarity(original_title, movie_item.title), score)
                    if aka:
                        for t in aka:
                            score = max(calc_similarity(t, movie_item.title), score)
                    if movie_item.year and year and movie_item.year == year:
                        score += 1
                    if movie_item.countries and countries:
                        for country in movie_item.countries:
                            if country in countries:
                                score += 1
                    if movie_item.directors and directors:
                        for director in movie_item.directors:
                            if director in directors:
                                score += 1
                    if movie_item.casts and casts:
                        for cast in movie_item.casts:
                            if cast in casts:
                                score += 1

                    if score > max_score:
                        max_score = score
                        max_movie = r

                if max_movie:
                    mongodb['movies'].update({'_id': ObjectId(max_movie.get('_source').get('_id'))},
                                             {'$set': {'resources.online.%s' % movie_item.provider: {'url': movie_item.url, 'similarity': max_score, 'last_updated': datetime.datetime.utcnow()}}})
                    self.logger.info('%s(%s) %s(douban) %s(similarity)', movie_item.title, movie_item.provider, max_movie.get('_source').get('title'), max_score)
                else:
                    self.logger.warn('No similar movie for %s(%s)', movie_item.title, movie_item.provider)
            except PyMongoError, e:
                self.logger.error('Mongodb error %s' % e)
            except Exception, e:
                self.logger.error(e)

class MovieItem(object):
    def __init__(self, provider, url, title, year=None, countries=None, directors=None, casts=None):
        self.provider = provider
        self.url = url
        self.title = title
        self.year = year
        self.countries = countries
        self.directors = directors
        self.casts = casts

if __name__ == '__main__':
    threads = [
        IQIYIMovieCrawler(),
        PPTVMovieCrawler(),
        OnlineMovieMatcher()
    ]
    for thread in threads:
        thread.start()
