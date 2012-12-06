# -*- coding: utf-8 -*-

'''
Created on Nov 25, 2012

@author: Fang Jiaguo
'''

from lxml.html import fromstring
from mongodb import movies_store_collection, movies_unmatched_collection
from pymongo.errors import PyMongoError
from urllib2 import HTTPError, URLError
from utils import request
from utils.log import log
import datetime
import time

class PPTVCrawler(object):
    '''
    Crawler for PPTV move site (http://movie.pptv.com/).
    '''

    logger = log.get_child_logger('PPTVCrawler')

    def __init__(self, sleep_time):
        self.__sleep_time = sleep_time

    def start_crawl(self):
        page_index = 0
        crawled_movies = 1
        while True:
            page_index += 1
            try:
                #====================================================================================================
                # Step 1: Crawl 'movie list page' with URL pattern <http://list.pptv.com/sort_list/1---------%s.html>
                #====================================================================================================
                url = 'http://list.pptv.com/sort_list/1---------%s.html' % page_index
                response = request.get(url, retry_interval=self.__sleep_time)
                response_text = response.read()#.decode('utf-8', 'ignore')
                PPTVCrawler.logger.info('Crawled <%s>' % url)
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
                    if url.startswith('http://v.pptv.com/show/'):
                        response = request.get(url, retry_interval=self.__sleep_time)
                        response_text = response.read()#.decode('utf-8', 'ignore')
                        PPTVCrawler.logger.info('Crawled <%s>' % url)
                        if self.__sleep_time > 0:
                            time.sleep(self.__sleep_time)

                        html_element = fromstring(response_text)
                        # Extract movie title element.
                        movie_title_elements = html_element.xpath('/html/body/div/div/div[@class="sbox showinfo"]/div[@class="bd"]/ul/li[1]/h3/a[@href]')

                        if movie_title_elements:
                            # Extract 'year' field.
                            movie_year = movie_title_elements[0].tail.strip()[1:-1].strip()
                            #===========================================================================================================================
                            # Step 3: Enter 'details page' with URL pattern <http://www.pptv.com/page/blabla> to extract 'title' and 'definition' fields
                            #===========================================================================================================================
                            url = movie_title_elements[0].attrib['href']
                            if url.startswith('http://www.pptv.com/page/'):
                                response = request.get(url, retry_interval=self.__sleep_time)
                                response_text = response.read()#.decode('utf-8', 'ignore')
                                PPTVCrawler.logger.info('Crawled <%s>' % url)
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
                                    PPTVCrawler.logger.info('Crawled movie #%s <%s %s %s>' % (crawled_movies, movie_year, movie_title, movie_definition))
                                    crawled_movies += 1
                                    #--------------------Update Mongodb--------------------------------------------
                                    # Match the movie info with douban in collection 'movies.store'.
                                    result = movies_store_collection.find_and_modify(query={'year': movie_year, '$or': [{'title': movie_title}, {'alt_titles': movie_title}]},
                                                                                     update={'$set': {'pptv.link': movie_element.attrib['href'], 'pptv.definition': movie_definition, 'pptv.last_updated': datetime.datetime.utcnow()}, '$inc': {'pptv.play_times': 0}},
                                                                                     fields={'_id': 1})
                                    if result:
                                        PPTVCrawler.logger.info('Matched with douban')
                                    else:
                                        # If we cannot find the matching, it means this movie has not yet been crawled
                                        # from douban, or douban does not contain related record of this movie. Then we
                                        # store movie info temporarily in collection 'movie.unmatched'.
                                        movies_unmatched_collection.update({'year': movie_year, 'title': movie_title, 'source': 'pptv'},
                                                                           {'$set': {'definition': movie_definition, 'link': movie_element.attrib['href'], 'last_updated': datetime.datetime.utcnow()}},
                                                                           upsert=True)
                                        PPTVCrawler.logger.info('Not matched with douban')
                                    #------------------------------------------------------------------------------
                                else:
                                    PPTVCrawler.logger.warning('Movie title not found on details page <%s>' % movie_title_elements[0].attrib['href'])
                            else:
                                PPTVCrawler.logger.warning('Invalid details page URL pattern <%s> on playing page <%s>' % (movie_title_elements[0].attrib['href'], movie_element.attrib['href']))
                        else:
                            PPTVCrawler.logger.warning('Details page link not found on playing page <%s>' % movie_element.attrib['href'])
                    else:
                        PPTVCrawler.logger.warning('Invalid playing page URL pattern <%s>' % movie_element.attrib['href'])

            except HTTPError, e:
                PPTVCrawler.logger.error('Server cannot fulfill the request <%s HTTP Error %s: %s>' % (url, e.code, e.msg))
            except URLError, e:
                PPTVCrawler.logger.error('Failed to reach server <%s Reason: %s>' % (url, e.reason))
            except PyMongoError, e:
                PPTVCrawler.logger.error('Mongodb error: %s <%s>' % (e, url))
            except Exception, e:
                PPTVCrawler.logger.error('Unknow exception: %s <%s>' % (e, url))

if __name__ == '__main__':
    pc = PPTVCrawler(1.5)
    pc.start_crawl()
