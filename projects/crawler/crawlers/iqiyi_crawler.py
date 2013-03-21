# -*- coding: utf-8 -*-

'''
Created on Dec 7, 2012

@author: Fang Jiaguo
'''
from lxml.html import fromstring
from pymongo.errors import PyMongoError
from sets import Set
from settings import settings, mongodb
from urllib2 import HTTPError, URLError
from urlparse import urlparse, urlunparse
from utilities import LimitedCaller, request, get_logger
import datetime
import logging
import re
import threading
import time

iqiyi_logger = get_logger('IQIYICrawler', 'iqiyi_crawler.log')
movie_regex = re.compile(settings['iqiyi_crawler']['movie_regex'])
vip_movie_regex = re.compile(settings['iqiyi_crawler']['vip_movie_regex'])
request_iqiyi_page = LimitedCaller(request.get, 60, settings['iqiyi_crawler']['reqs_per_min'])

class IQIYICrawler(object):
    '''
    Crawler for iqiyi movie.
    '''

    def start(self):
        threads = [
            MovieCrawler(),
        ]
        for thread in threads:
            thread.start()

class MovieCrawler(threading.Thread):
    def run(self):
        logger = logging.getLogger('IQIYICrawler.MovieCrawler')
        crawled_urls = Set()
        while True:
            logger.info('==========MovieCrawler Started==========')
            page_index = 1
            crawled_urls.clear()  # !important

            while True:
                try:
                    page = settings['iqiyi_crawler']['movie_crawler']['page'] % page_index
                    page_index += 1
                    response = request_iqiyi_page(page.encode('utf-8'))
                    response_text = response.read()
                    logger.debug('Crawled <%s>' % page)

                    find_movie = False
                    html_element = fromstring(response_text)
                    link_elements = html_element.xpath('//a[@href and @class="title"]')
                    for link_element in link_elements:
                        # special case for VIP URL: http://www.iqiyi.com/dianying/20121208/376949c91b2ab1bc.html?fc=a64f3700229a0bc3
                        scheme, netloc, path, _, _, _ = urlparse(link_element.attrib['href'])
                        url = urlunparse((scheme, netloc, path, None, None, None))
                        if url not in crawled_urls and (movie_regex.match(url) or vip_movie_regex.match(url)):
                            find_movie = True
                            crawled_urls.add(url)
                            title = link_element.text.strip()
                            try:
                                result = mongodb['movies'].find_and_modify(query={'$or': [{'title': title}, {'original_title': title}, {'aka': title}]},
                                                                           update={'$addToSet': {'online': {'source': 'iqiyi', 'title': title, 'url': url}}},
                                                                           fields={'_id': 1})
                                if result:
                                    logger.info('Match with douban <%s>' % title)
                                else:
                                    logger.info('Cannot match with douban <%s>' % title)

                            except PyMongoError, e:
                                logger.error('Mongodb error <%s>' % e)
                                continue

                    if not find_movie:
                        break

                except HTTPError, e:
                    logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (page, e.code, e.msg))
                except URLError, e:
                    logger.error('Failed to reach server <%s> <%s>' % (page, e.reason))
                except Exception, e:
                    logger.error('%s <%s>' % (e, page))

            logger.info('==========MovieCrawler Finished=========')

            # sleep till next run
            hour, minute = tuple(settings['iqiyi_crawler']['movie_crawler']['run_at'].split(':'))
            now = datetime.datetime.utcnow()
            next_run = datetime.datetime(now.year, now.month, now.day, int(hour), int(minute), now.second) + datetime.timedelta(days=1)  # calculate next run time
            time.sleep((next_run - now).total_seconds())
