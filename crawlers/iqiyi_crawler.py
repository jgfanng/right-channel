# -*- coding: utf-8 -*-

'''
Created on Dec 7, 2012

@author: Fang Jiaguo
'''
from crawlers.exceptions import CrawlerError
from crawlers.mongodb import movies_store_collection, \
    movies_unmatched_collection
from lxml.html import fromstring
from pymongo.errors import PyMongoError
from urllib2 import HTTPError, URLError
from utils import request
from utils.log import get_logger
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

        page_index = 0
        while True:
            page_index += 1
            try:
                movie_list_page_url = 'http://list.iqiyi.com/www/1/------------2-1-%s-1---.html' % page_index
                response = request.get(movie_list_page_url, retry_interval=self.__sleep_time)
                response_text = response.read()
                IQIYICrawler.logger.debug('Crawled <%s>' % movie_list_page_url)
                if self.__sleep_time > 0:
                    time.sleep(self.__sleep_time)

                html_element = fromstring(response_text)
                movie_elements = html_element.xpath('/html/body/div/div/div/div/div/div/ul[@class="ulList dianying"]/li[@class="j-listanim"]/a[@class="title" and @href]')

                # If no links are found, finish crawling.
                if not movie_elements:
                    # Write log in case xpath changes. !important
                    IQIYICrawler.logger.warning('Movies not found on movie list page <%s>. Please check whether the xpath has changed' % movie_list_page_url)
                    break

                movie_definition_elements = html_element.xpath('/html/body/div/div/div/div/div/div/ul[@class="ulList dianying"]/li[@class="j-listanim"]/a/span[@class="cqBg"]')
                movie_definition = '超清' if movie_definition_elements else '一般'

                for movie_element in movie_elements:
                    playing_page_url = movie_element.attrib['href']
                    movie_title = movie_element.text.strip()
                    movie_year = self.__get_movie_year(playing_page_url)
                    # skip if no year found
                    if not movie_year:
                        continue
                    movie_intro_elements = html_element.xpath('/html/body/div/div/div/div/div/div/ul[@class="ulList dianying"]/li[@class="j-listanim"]/div[@class="popUp"]/div[@class="pop-bottom-con"]/a[@href]')
                    if movie_intro_elements:
                        # more accurate title on introduction page
                        title_on_intro_page = self.__get_movie_title(movie_intro_elements[0].attrib['href'])
                        if title_on_intro_page:
                            movie_title = title_on_intro_page

                    self.__total_movies_crawled += 1
                    IQIYICrawler.logger.info('Crawled movie #%s <%s %s %s>' % (self.__total_movies_crawled, movie_year, movie_title, movie_definition))

                    #--------------------Save to Mongodb-------------------------------------------
                    result = movies_store_collection.find_and_modify(query={'year': movie_year, '$or': [{'title': movie_title}, {'alt_titles': movie_title}]},
                                                                     update={'$set': {'iqiyi.link': playing_page_url, 'iqiyi.definition': movie_definition, 'iqiyi.last_updated': datetime.datetime.utcnow()}, '$inc': {'iqiyi.play_times': 0}},
                                                                     fields={'_id': 1})
                    if result:
                        IQIYICrawler.logger.debug('Matched with douban')
                    else:
                        movies_unmatched_collection.update({'year': movie_year, 'title': movie_title, 'source': 'iqiyi'},
                                                           {'$set': {'definition': movie_definition, 'link': playing_page_url, 'last_updated': datetime.datetime.utcnow()}},
                                                           upsert=True)
                        IQIYICrawler.logger.debug('Not matched with douban')
                    #------------------------------------------------------------------------------

            except CrawlerError, e:
                IQIYICrawler.logger.error(e)
            except HTTPError, e:
                IQIYICrawler.logger.error('Server cannot fulfill the request <%s HTTP Error %s: %s>' % (movie_list_page_url, e.code, e.msg))
            except URLError, e:
                IQIYICrawler.logger.error('Failed to reach server <%s Reason: %s>' % (movie_list_page_url, e.reason))
            except PyMongoError, e:
                IQIYICrawler.logger.error('%s <%s>' % (e, playing_page_url))
            except Exception, e:
                IQIYICrawler.logger.error('%s <%s>' % (e, movie_list_page_url))

    def __get_movie_year(self, playing_page_url):
        '''
        Get movie year on playing page.
        '''

        try:
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
                # Write log in case xpath changes. !important
                IQIYICrawler.logger.warning('Movie year not found on playing page <%s>. Please check whether the xpath has changed' % playing_page_url)
                return None

        except HTTPError, e:
            raise CrawlerError('Server cannot fulfill the request <%s HTTP Error %s: %s>' % (playing_page_url, e.code, e.msg))
        except URLError, e:
            raise CrawlerError('Failed to reach server <%s Reason: %s>' % (playing_page_url, e.reason))
        except Exception, e:
            raise CrawlerError('%s <%s>' % (e, playing_page_url))

    def __get_movie_title(self, intro_page_url):
        '''
        Get movie title on introduction page.
        '''

        try:
            response = request.get(intro_page_url, retry_interval=self.__sleep_time)
            response_text = response.read().decode('utf-8', 'ignore')
            IQIYICrawler.logger.debug('Crawled <%s>' % intro_page_url)
            if self.__sleep_time > 0:
                time.sleep(self.__sleep_time)

            html_element = fromstring(response_text)
            movie_title_elements = html_element.xpath('/html/body/div/div/div/div/div/div[@class="prof-title"]/h1')
            if movie_title_elements:
                return movie_title_elements[0].text.strip()
            else:
                # Write log in case xpath changes. !important
                IQIYICrawler.logger.warning('Movie title not found on introduction page <%s>. Please check whether the xpath has changed' % intro_page_url)
                return None

        except HTTPError, e:
            raise CrawlerError('Server cannot fulfill the request <%s HTTP Error %s: %s>' % (intro_page_url, e.code, e.msg))
        except URLError, e:
            raise CrawlerError('Failed to reach server <%s Reason: %s>' % (intro_page_url, e.reason))
        except Exception, e:
            raise CrawlerError('%s <%s>' % (e, intro_page_url))

if __name__ == '__main__':
    ic = IQIYICrawler(1)
    ic.start_crawl()
