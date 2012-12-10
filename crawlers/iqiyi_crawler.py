# -*- coding: utf-8 -*-

'''
Created on Dec 7, 2012

@author: Fang Jiaguo
'''
from crawlers.exceptions import MovieYearNotFoundError, MovieTitleNotFoundError
from crawlers.mongodb import movies_store_collection, movies_unmatched_collection
from crawlers.utils import request
from crawlers.utils.log import get_logger
from lxml.html import fromstring
from pymongo.errors import PyMongoError
from urllib2 import HTTPError, URLError
import datetime
import time

class IQIYICrawler(object):
    '''
    Crawler for iqiyi movie (http://www.iqiyi.com/dianying/).
    '''

    logger = get_logger('IQIYICrawler', 'iqiyi_crawler.log')

    def __init__(self, sleep_time):
        self.__sleep_time = sleep_time
        self.__total_movies_crawled = 0

    def start_crawl(self):
        IQIYICrawler.logger.info('==========Start to crawl iqiyi movies==========')
        self.__start_crawl()
        IQIYICrawler.logger.info('==========Finish crawling iqiyi movies==========')
        IQIYICrawler.logger.info('==========Totally crawled %s movies==========' % self.__total_movies_crawled)

    def __start_crawl(self):
        '''
        Crawl 'movie list page' with URL pattern <http://list.iqiyi.com/www/1/------------2-1-%s-1---.html>
        '''

        page_index = 1
        while True:
            try:
                movie_list_page_url = 'http://list.iqiyi.com/www/1/------------2-1-%s-1---.html' % page_index
                page_index += 1
                response = request.get(movie_list_page_url, retry_interval=self.__sleep_time)
                response_text = response.read()
                IQIYICrawler.logger.debug('Crawled <%s>' % movie_list_page_url)
                if self.__sleep_time > 0:
                    time.sleep(self.__sleep_time)

                html_element = fromstring(response_text)
                movie_elements = html_element.xpath('/html/body/div/div/div/div/div/div/ul[@class="ulList dianying"]/li[@class="j-listanim"]')

                # If no links are found, finish crawling.
                if not movie_elements:
                    IQIYICrawler.logger.warning('Movies not found on movie list page <%s>. Please check whether the xpath has changed' % movie_list_page_url)
                    break

                for movie_element in movie_elements:
                    #----------get playing page URL--------------------------
                    movie_title_elements = movie_element.xpath('./a[@class="title" and @href]')
                    if movie_title_elements:
                        playing_page_url = movie_title_elements[0].attrib['href']
                    else:
                        IQIYICrawler.logger.warning('Playing page URL not found on movie list page <%s>. Please check whether the xpath has changed' % movie_list_page_url)
                        continue

                    #----------get movie year on playing page----------------
                    try:
                        movie_year = self.__get_movie_year(playing_page_url)
                    except MovieYearNotFoundError, e:
                        IQIYICrawler.logger.warning('Movie year not found on playing page <%s>. Please check whether the xpath has changed' % playing_page_url)
                        continue
                    except HTTPError, e:
                        IQIYICrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (playing_page_url, e.code, e.msg))
                        continue
                    except URLError, e:
                        IQIYICrawler.logger.error('Failed to reach server <%s %s>' % (playing_page_url, e.reason))
                        continue
                    except Exception, e:
                        IQIYICrawler.logger.error('%s <%s>' % (e, playing_page_url))
                        continue

                    #----------get introduction page URL---------------------
                    movie_intro_elements = movie_element.xpath('./div[@class="popUp"]/div[@class="pop-bottom-con"]/a[@href]')
                    if movie_intro_elements:
                        # more accurate title on introduction page
                        intro_page_url = movie_intro_elements[0].attrib['href']
                    else:
                        IQIYICrawler.logger.warning('Introduction page URL not found on movie list page <%s>. Please check whether the xpath has changed' % movie_list_page_url)
                        continue

                    #----------get movie title on introduction page----------
                    try:
                        movie_title = self.__get_movie_title(intro_page_url)
                    except MovieTitleNotFoundError, e:
                        IQIYICrawler.logger.warning('Movie title not found on introduction page <%s>. Please check whether the xpath has changed' % intro_page_url)
                        continue
                    except HTTPError, e:
                        IQIYICrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (intro_page_url, e.code, e.msg))
                        continue
                    except URLError, e:
                        IQIYICrawler.logger.error('Failed to reach server <%s %s>' % (intro_page_url, e.reason))
                        continue
                    except Exception, e:
                        IQIYICrawler.logger.error('%s <%s>' % (e, intro_page_url))
                        continue

                    #----------get movie definition--------------------------
                    movie_definition_elements = movie_element.xpath('./a/span[@class="cqBg"]')
                    movie_definition = '超清' if movie_definition_elements else '一般'

                    #----------Save to Mongodb-------------------------------
                    try:
                        source_name = 'iqiyi'
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
                                                               {'$push': {'name': source_name, 'definition': movie_definition, 'link': playing_page_url, 'play_times': 0, 'last_updated': datetime.datetime.utcnow()}})
                            IQIYICrawler.logger.debug('Matched with douban')
                        else:
                            movies_unmatched_collection.update({'year': movie_year, 'title': movie_title, 'source': 'iqiyi'},
                                                               {'$set': {'definition': movie_definition, 'link': playing_page_url, 'last_updated': datetime.datetime.utcnow()}},
                                                               upsert=True)
                            IQIYICrawler.logger.debug('Not matched with douban')

                    except PyMongoError, e:
                        IQIYICrawler.logger.error('%s <%s %s>' % (e, movie_year, movie_title))
                        continue
                    #--------------------------------------------------------

                    self.__total_movies_crawled += 1
                    IQIYICrawler.logger.info('Crawled movie #%s <%s %s %s>' % (self.__total_movies_crawled, movie_year, movie_title, movie_definition))

            except HTTPError, e:
                IQIYICrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (movie_list_page_url, e.code, e.msg))
            except URLError, e:
                IQIYICrawler.logger.error('Failed to reach server <%s %s>' % (movie_list_page_url, e.reason))
            except Exception, e:
                IQIYICrawler.logger.error('%s <%s>' % (e, movie_list_page_url))

    def __get_movie_year(self, playing_page_url):
        '''
        Get movie year on playing page.
        '''

        response = request.get(playing_page_url, retry_interval=self.__sleep_time)
        response_text = response.read()
        IQIYICrawler.logger.debug('Crawled <%s>' % playing_page_url)
        if self.__sleep_time > 0:
            time.sleep(self.__sleep_time)

        html_element = fromstring(response_text)
        movie_year_elements = html_element.xpath('/html/body/div/div/h1[@id="navbar"]/span/a')
        if movie_year_elements:
            return movie_year_elements[0].text.strip()
        else:
            raise MovieYearNotFoundError()

    def __get_movie_title(self, intro_page_url):
        '''
        Get movie title on introduction page.
        '''

        response = request.get(intro_page_url, retry_interval=self.__sleep_time)
        response_text = response.read()
        IQIYICrawler.logger.debug('Crawled <%s>' % intro_page_url)
        if self.__sleep_time > 0:
            time.sleep(self.__sleep_time)

        html_element = fromstring(response_text.decode('utf-8', 'ignore'))
        movie_title_elements = html_element.xpath('/html/body/div/div/div/div/div/div[@class="prof-title"]/h1')
        if movie_title_elements:
            return movie_title_elements[0].text.strip()
        else:
            raise MovieTitleNotFoundError()

if __name__ == '__main__':
    ic = IQIYICrawler(1)
    ic.start_crawl()
