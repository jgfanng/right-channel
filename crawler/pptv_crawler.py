# -*- coding: utf-8 -*-

'''
Created on Nov 25, 2012

@author: Fang Jiaguo
'''

from lxml.html import fromstring
from pymongo.errors import PyMongoError
from urllib2 import HTTPError, URLError
from utils import request
from utils.log import log
import time

class PPTVCrawler(object):
    '''
    Crawler for PPTV move site (http://movie.pptv.com/).
    '''

    def __init__(self, sleep_time):
        self.__sleep_time = sleep_time

    def start_crawl(self):
        page_index = 0
        while True:
            page_index += 1
            try:
                #====================================================================================================
                # Step 1: Crawl 'movie list page' with URL pattern <http://list.pptv.com/sort_list/1---------%s.html>
                #====================================================================================================
                url = 'http://list.pptv.com/sort_list/1---------%s.html' % page_index
                response = request.get(url, retry_interval=self.__sleep_time)
                response_text = response.read().decode('utf-8', 'ignore')
                log.info('Crawled <%s>' % url)
                if self.__sleep_time > 0:
                    time.sleep(self.__sleep_time)

                html_element = fromstring(response_text)
                # Extract all links in the document.
                movie_elements = html_element.xpath('/html/body/div/div/div/div[@class="bd"]/ul/li/p[@class="txt"]/a[@href]')

                # If no links found, then finish crawling.
                if not movie_elements:
                    break

                #======================================================================================================
                # Step 2: Enter 'playing page' with URL pattern <http://v.pptv.com/show/blabla> to extract 'year' field
                #======================================================================================================
                for movie_element in movie_elements:
                    url = movie_element.attrib['href']
                    if url.startswith('http://v.pptv.com/show'):
                        response = request.get(url, retry_interval=self.__sleep_time)
                        response_text = response.read().decode('utf-8', 'ignore')
                        log.info('Crawled <%s>' % url)
                        if self.__sleep_time > 0:
                            time.sleep(self.__sleep_time)

                        html_element = fromstring(response_text)
                        # Extract movie title element.
                        movie_title_elements = html_element.xpath('/html/body/div/div/div[@class="sbox showinfo"]/div[@class="bd"]/ul/li[1]/h3/a[@href]')

                        if movie_title_elements:
                            # Extract 'year' field.
                            movie_year = movie_title_elements[0].tail.strip()[1:-1]
                            #===========================================================================================================================
                            # Step 3: Enter 'details page' with URL pattern <http://www.pptv.com/page/blabla> to extract 'title' and 'definition' fields
                            #===========================================================================================================================
                            url = movie_title_elements[0].attrib['href']
                            if url.startswith('http://www.pptv.com/page'):
                                response = request.get(url, retry_interval=self.__sleep_time)
                                response_text = response.read().decode('utf-8', 'ignore')
                                log.info('Crawled <%s>' % url)
                                if self.__sleep_time > 0:
                                    time.sleep(self.__sleep_time)

                                html_element = fromstring(response_text)
                                # Extract actual movie title element.
                                actual_movie_title_elements = html_element.xpath('/html/body/div/span[@class="crumb_current"]')

                                if actual_movie_title_elements:
                                    movie_title = actual_movie_title_elements[0].text.strip()
                                    movie_definition = 'Unknown'
                                    movie_definition_elements = html_element.xpath('/html/body/div/p[@class="tabs"]/em')
                                    for element in movie_definition_elements:
                                        if element.text.strip().startswith(u'清晰度：'):
                                            movie_definition = element.text.strip()[len(u'清晰度：'):]
                                            break
                                    log.info('Crawled movie "%s %s %s"' % (movie_year, movie_title, movie_definition))
                                else:
                                    log.warning('Movie title not found on details page <%s>' % movie_title_elements[0].attrib['href'])
                            else:
                                log.warning('Invalid details page URL pattern <%s> on playing page <%s>' % (movie_title_elements[0].attrib['href'], movie_element.attrib['href']))
                        else:
                            log.warning('Details page link not found on playing page <%s>' % movie_element.attrib['href'])
                    else:
                        log.warning('Invalid playing page URL pattern on playing page <%s>' % movie_element.attrib['href'])

            except HTTPError, e:
                log.error('Server cannot fulfill the request <%s HTTP Error %s: %s>' % (url, e.code, e.msg))
            except URLError, e:
                log.error('Failed to reach server <%s Reason: %s>' % (url, e.reason))
            except PyMongoError, e:
                log.error('Mongodb error: %s <%s>' % (e, url))
            except Exception, e:
                log.error('Unknow exception: %s <%s>' % (e, url))

if __name__ == '__main__':
    pc = PPTVCrawler(2)
    pc.start_crawl()
