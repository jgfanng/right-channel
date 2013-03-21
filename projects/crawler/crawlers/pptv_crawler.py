# -*- coding: utf-8 -*-

'''
Created on Nov 25, 2012

@author: Fang Jiaguo
'''
from lxml.html import fromstring
from pymongo.errors import PyMongoError
from sets import Set
from settings import settings, mongodb
from urllib2 import HTTPError, URLError
from utilities import LimitedCaller, request, get_logger
import datetime
import logging
import re
import threading
import time

pptv_logger = get_logger('PPTVCrawler', 'pptv_crawler.log')
movie_regex = re.compile(settings['pptv_crawler']['movie_regex'])
request_pptv_page = LimitedCaller(request.get, 60, settings['pptv_crawler']['reqs_per_min'])

class PPTVCrawler(object):
    '''
    Crawler for pptv movie.
    '''

    def start(self):
        threads = [
            MovieCrawler(),
        ]
        for thread in threads:
            thread.start()

class MovieCrawler(threading.Thread):
    def run(self):
        logger = logging.getLogger('PPTVCrawler.MovieCrawler')
        crawled_urls = Set()
        while True:
            logger.info('==========MovieCrawler Started==========')
            page_index = 1
            crawled_urls.clear()  # !important

            while True:
                try:
                    page = settings['pptv_crawler']['movie_crawler']['page'] % page_index
                    page_index += 1
                    response = request_pptv_page(page.encode('utf-8'))
                    response_text = response.read()
                    logger.debug('Crawled <%s>' % page)

                    find_movie = False
                    html_element = fromstring(response_text)
                    link_elements = html_element.xpath('//a[@href]')
                    for link_element in link_elements:
                        try:
                            title = link_element.text
                            url = link_element.attrib['href']
                            m = movie_regex.match(url)
                            if title and url not in crawled_urls and m:
                                find_movie = True
                                crawled_urls.add(url)
                                title = title.strip()

                                result = mongodb['movies'].find_and_modify(query={'$or': [{'title': title}, {'original_title': title}, {'aka': title}]},
                                                                           update={'$set': {'online.pptv': {'id': m.groupdict().get('id'), 'title': title, 'url': url, 'last_updated': datetime.datetime.utcnow()}}},
                                                                           fields={'_id': 1})
                                if result:
                                    logger.info('Match with douban <%s>' % title)
                                else:
                                    logger.info('Cannot match with douban <%s>' % title)

                        except PyMongoError, e:
                            logger.error('Mongodb error <%s>' % e)
                        except Exception, e:
                            logger.error('%s <%s>' % (e, page))

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
            hour, minute = tuple(settings['pptv_crawler']['movie_crawler']['run_at'].split(':'))
            now = datetime.datetime.utcnow()
            next_run = datetime.datetime(now.year, now.month, now.day, int(hour), int(minute), now.second) + datetime.timedelta(days=1)  # calculate next run time
            time.sleep((next_run - now).total_seconds())
