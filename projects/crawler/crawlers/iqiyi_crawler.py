# -*- coding: utf-8 -*-

'''
Created on Dec 7, 2012

@author: Fang Jiaguo
'''
from lxml.html import fromstring
from sets import Set
from settings import settings
from urllib2 import HTTPError, URLError
from urlparse import urlparse, urlunparse
from utilities import LimitedCaller, get_logger, send_request, get_child_logger
import re
import threading

movie_regex = re.compile(settings['iqiyi_crawler']['movie_regex'])
vip_movie_regex = re.compile(settings['iqiyi_crawler']['vip_movie_regex'])
request_iqiyi_page = LimitedCaller(send_request, settings['iqiyi_crawler']['reqs_per_min'])

class IQIYICrawler(object):
    def __init__(self):
        self.logger = get_logger('IQIYICrawler', 'iqiyi_crawler.log')

    def start(self):
        threads = [
            MovieCrawler(),
        ]
        for thread in threads:
            thread.start()

class MovieCrawler(threading.Thread):
    def __init__(self):
        self.logger = get_child_logger('IQIYICrawler', 'MovieCrawler')
        threading.Thread.__init__(self)

    def run(self):
        self.logger.info('==========MovieCrawler Started==========')

        page_index = 0
        crawled_urls = Set()
        while True:
            try:
                page_index += 1
                page = settings['iqiyi_crawler']['movie_crawler']['page'] % page_index
                response = request_iqiyi_page(page.encode('utf-8'))
                response_text = response.read()
                self.logger.debug('Crawled <%s>' % page)
                html_element = fromstring(response_text)
                link_elements = html_element.xpath('//a[@href]')

                find_movie = False
                for link_element in link_elements:
                    title = link_element.text
                    scheme, netloc, path, _, _, _ = urlparse(link_element.attrib['href'])
                    url = urlunparse((scheme, netloc, path, None, None, None))  # remove query string
                    if title and title.strip() and url not in crawled_urls and (movie_regex.match(url) or vip_movie_regex.match(url)):
                        find_movie = True
                        crawled_urls.add(url)
                        title = title.strip()
                        try:
                            directors = None; casts = None
                            response = request_iqiyi_page(url.encode('utf-8'))  # request playing page to get (countries, directors, casts)
                            response_text = response.read()
                            self.logger.debug('Crawled <%s>' % url)
                            html_element = fromstring(response_text)
                            directors_elements = html_element.xpath(u'//*[normalize-space(text())="导演："]')
                            if directors_elements:
                                directors_element = directors_elements[0]
                                directors = [director.strip() for director in (directors_element.xpath('./a/text()') or directors_element.xpath('../a/text()')) if director.strip() != '展开']  # special case
                            casts_elements = html_element.xpath(u'//*[normalize-space(text())="主演："]')
                            if casts_elements:
                                casts_element = casts_elements[0]
                                casts = [cast.strip() for cast in (casts_element.xpath('./a/text()') or casts_element.xpath('../a/text()')) if cast.strip() != '展开']  # special case
                        except HTTPError, e:
                            self.logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (url, e.code, e.msg))
                        except URLError, e:
                            self.logger.error('Failed to reach server <%s> <%s>' % (url, e.reason))
                        except Exception, e:
                            self.logger.error('%s <%s>' % (e, url))

                        self.logger.info('Crawled movie <%s, %s, %s>' % (title, ' '.join(directors) if directors else None, ' '.join(casts) if casts else None))

                if not find_movie:
                    break

            except HTTPError, e:
                self.logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (page, e.code, e.msg))
            except URLError, e:
                self.logger.error('Failed to reach server <%s> <%s>' % (page, e.reason))
            except Exception, e:
                self.logger.error('%s <%s>' % (e, page))

        self.logger.info('==========MovieCrawler Finished=========')
