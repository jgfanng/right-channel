# -*- coding: utf-8 -*-

'''
Created on Nov 25, 2012

@author: Fang Jiaguo
'''
from crawlers.base_crawler import BaseCrawler
from lxml.html import fromstring
from pymongo.errors import PyMongoError
from sets import Set
from settings import settings
from urllib2 import HTTPError, URLError
from utilities import LimitedCaller, get_logger, send_request
import logging
import re
import threading

pptv_logger = get_logger('PPTVCrawler', 'pptv_crawler.log')
movie_regex = re.compile(settings['pptv_crawler']['movie_regex'])
request_pptv_page = LimitedCaller(send_request, settings['pptv_crawler']['reqs_per_min'])

class PPTVCrawler(BaseCrawler):
    def start(self):
        threads = [
            MovieCrawler(),
        ]
        for thread in threads:
            thread.start()

class MovieCrawler(threading.Thread):
    def __init__(self):
        self.logger = logging.getLogger('PPTVCrawler.MovieCrawler')
        threading.Thread.__init__(self)

    def run(self):
        self.logger.info('==========MovieCrawler Started==========')

        page_index = 0
        crawled_urls = Set()
        while True:
            try:
                page_index += 1
                page = settings['pptv_crawler']['movie_crawler']['page'] % page_index
                response = request_pptv_page(page.encode('utf-8'))
                response_text = response.read()
                self.logger.debug('Crawled <%s>' % page)
                html_element = fromstring(response_text)
                link_elements = html_element.xpath('//a[@href]')

                find_movie = False
                for link_element in link_elements:
                    try:
                        title = link_element.text  # text may be corrupted
                        url = link_element.attrib['href']
                        match = movie_regex.match(url)
                        if title and title.strip() and match and url not in crawled_urls:  # filter image URL
                            find_movie = True
                            crawled_urls.add(url)
                            title = title.strip()

                            self.logger.info('Crawled <%s, %s, %s, %s>' % (title, countries, directors, casts))

                    except PyMongoError, e:
                        self.logger.error('Mongodb error <%s>' % e)
                    except Exception, e:
                        self.logger.error('%s <%s>' % (e, page))

                if not find_movie:
                    break

            except HTTPError, e:
                self.logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (page, e.code, e.msg))
            except URLError, e:
                self.logger.error('Failed to reach server <%s> <%s>' % (page, e.reason))
            except Exception, e:
                self.logger.error('%s <%s>' % (e, page))

        self.logger.info('==========MovieCrawler Finished=========')
