# -*- coding: utf-8 -*-

'''
Created on Nov 25, 2012

@author: Fang Jiaguo
'''
from crawlers.utils import request
from crawlers.utils.exceptions import MovieYearNotFoundError, \
    MovieTitleNotFoundError
from crawlers.utils.log import get_logger
from crawlers.utils.mongodb import movies_store_collection, \
    movies_unmatched_collection
from lxml.html import fromstring
from pymongo.errors import PyMongoError
from urllib2 import HTTPError, URLError
import datetime
import time

class PPTVCrawler(object):
    '''
    Crawler for pptv move (http://movie.pptv.com/).
    '''

    logger = get_logger('PPTVCrawler', 'pptv_crawler.log')

    def __init__(self, sleep_time):
        self.__sleep_time = sleep_time
        self.__total_movies_crawled = 0

    def start_crawl(self):
        PPTVCrawler.logger.info('==========Start to crawl pptv movies==========')
        self.__start_crawl()
        PPTVCrawler.logger.info('==========Finish crawling pptv movies==========')
        PPTVCrawler.logger.info('==========Totally crawled %s movies==========' % self.__total_movies_crawled)

    def __start_crawl(self):
        '''
        Crawl 'movie list page' with URL pattern <http://list.pptv.com/sort_list/1---------%s.html>
        '''

        page_index = 1
        while True:
            try:
                movie_list_page_url = 'http://list.pptv.com/sort_list/1---------%s.html' % page_index
                page_index += 1
                response = request.get(movie_list_page_url, retry_interval=self.__sleep_time)
                response_text = response.read()
                PPTVCrawler.logger.debug('Crawled <%s>' % movie_list_page_url)
                if self.__sleep_time > 0:
                    time.sleep(self.__sleep_time)

                html_element = fromstring(response_text)
                movie_elements = html_element.xpath('/html/body/div/div/div/div[@class="bd"]/ul/li/p[@class="txt"]/a[@href]')

                # If no links are found, finish crawling.
                if not movie_elements:
                    PPTVCrawler.logger.warning('Movies not found on movie list page <%s>. Please check whether the xpath has changed' % movie_list_page_url)
                    break

                for movie_element in movie_elements:
                    #----------get movie year on playing page----------------
                    try:
                        playing_page_url = movie_element.attrib['href']
                        movie_year, details_page_url = self.__get_movie_year(playing_page_url)
                    except MovieYearNotFoundError, e:
                        PPTVCrawler.logger.warning('Movie year not found on playing page <%s>. Please check whether the xpath has changed' % playing_page_url)
                        continue
                    except HTTPError, e:
                        PPTVCrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (playing_page_url, e.code, e.msg))
                        continue
                    except URLError, e:
                        PPTVCrawler.logger.error('Failed to reach server <%s %s>' % (playing_page_url, e.reason))
                        continue
                    except Exception, e:
                        PPTVCrawler.logger.error('%s <%s>' % (e, playing_page_url))
                        continue

                    #----------get movie title, definition on details page----------
                    try:
                        movie_title, movie_definition = self.__get_movie_title_definition(details_page_url)
                    except MovieTitleNotFoundError, e:
                        PPTVCrawler.logger.warning('Movie title not found on details page <%s>. Please check whether the xpath has changed' % details_page_url)
                        continue
                    except HTTPError, e:
                        PPTVCrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (details_page_url, e.code, e.msg))
                        continue
                    except URLError, e:
                        PPTVCrawler.logger.error('Failed to reach server <%s %s>' % (details_page_url, e.reason))
                        continue
                    except Exception, e:
                        PPTVCrawler.logger.error('%s <%s>' % (e, details_page_url))
                        continue

                    #--------------------Save to Mongodb---------------------
                    try:
                        source_name = 'pptv'
                        result = movies_store_collection.find_one({'year': movie_year, '$or': [{'title': movie_title}, {'alt_titles': movie_title}]},
                                                                  fields={'_id': 1})
                        if result:
                            result = movies_store_collection.find_one({'year': movie_year, '$or': [{'title': movie_title}, {'alt_titles': movie_title}], 'sources.name': source_name},
                                                                      fields={'_id': 1})
                            if result:
                                movies_store_collection.update({'year': movie_year, '$or': [{'title': movie_title}, {'alt_titles': movie_title}], 'sources.name': source_name},
                                                               {'$set': {'sources.$.definition': movie_definition, 'sources.$.link': playing_page_url, 'sources.$.last_updated': datetime.datetime.utcnow()}})
                            else:
                                movies_store_collection.update({'year': movie_year, '$or': [{'title': movie_title}, {'alt_titles': movie_title}]},
                                                               {'$push': {'sources': {'name': source_name, 'definition': movie_definition, 'link': playing_page_url, 'play_times': 0, 'last_updated': datetime.datetime.utcnow()}}})
                            self.__total_movies_crawled += 1
                            PPTVCrawler.logger.info('Crawled movie #%s <%s %s %s> Matched' % (self.__total_movies_crawled, movie_year, movie_title, movie_definition))
                        else:
                            movies_unmatched_collection.update({'year': movie_year, 'title': movie_title, 'source': source_name},
                                                               {'$set': {'definition': movie_definition, 'link': playing_page_url, 'last_updated': datetime.datetime.utcnow()}},
                                                               upsert=True)
                            self.__total_movies_crawled += 1
                            PPTVCrawler.logger.info('Crawled movie #%s <%s %s %s> Unmatched' % (self.__total_movies_crawled, movie_year, movie_title, movie_definition))

                    except PyMongoError, e:
                        PPTVCrawler.logger.error('%s <%s %s>' % (e, movie_year, movie_title))
                        continue
                    #--------------------------------------------------------

            except HTTPError, e:
                PPTVCrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (movie_list_page_url, e.code, e.msg))
            except URLError, e:
                PPTVCrawler.logger.error('Failed to reach server <%s %s>' % (movie_list_page_url, e.reason))
            except Exception, e:
                PPTVCrawler.logger.error('%s <%s>' % (e, movie_list_page_url))

    def __get_movie_year(self, playing_page_url):
        '''
        Get movie year on playing page.
        '''

        response = request.get(playing_page_url, retry_interval=self.__sleep_time)
        response_text = response.read()
        PPTVCrawler.logger.debug('Crawled <%s>' % playing_page_url)
        if self.__sleep_time > 0:
            time.sleep(self.__sleep_time)

        html_element = fromstring(response_text)
        movie_title_elements = html_element.xpath('/html/body/div/div/div[@class="sbox showinfo"]/div[@class="bd"]/ul/li[1]/h3/a[@href]')
        if movie_title_elements:
            movie_year = movie_title_elements[0].tail
            if movie_year and movie_year.strip() and movie_year.startswith('(') and movie_year.endswith(')'):
                return movie_year[1:-1].strip(), movie_title_elements[0].attrib['href']
            else:
                raise MovieYearNotFoundError()
        else:
            raise MovieYearNotFoundError()

    def __get_movie_title_definition(self, details_page_url):
        '''
        Get movie title and definition on details page.
        '''

        #----------get movie title-------------------------------
        response = request.get(details_page_url, retry_interval=self.__sleep_time)
        response_text = response.read()
        PPTVCrawler.logger.debug('Crawled <%s>' % details_page_url)
        if self.__sleep_time > 0:
            time.sleep(self.__sleep_time)

        html_element = fromstring(response_text)
        movie_title_elements = html_element.xpath('/html/body/div/span[@class="crumb_current"]')
        if movie_title_elements:
            movie_title = movie_title_elements[0].text.strip()
        else:
            raise MovieTitleNotFoundError()

        #----------get movie definition--------------------------
        movie_definition = '一般'
        movie_definition_elements = html_element.xpath('/html/body/div/p[@class="tabs"]/em')
        for element in movie_definition_elements:
            if element.text.strip().startswith(u'清晰度：'):
                movie_definition = element.text.strip()[len(u'清晰度：'):]
                break

        return movie_title, movie_definition

if __name__ == '__main__':
    pc = PPTVCrawler(1)
    pc.start_crawl()
