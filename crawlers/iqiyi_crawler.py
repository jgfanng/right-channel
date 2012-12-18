# -*- coding: utf-8 -*-

'''
Created on Dec 7, 2012

@author: Fang Jiaguo
'''
from crawlers.utils import request
from crawlers.utils.log import get_logger
from crawlers.utils.mongodb import movie_source_collection
from lxml.html import fromstring
from pymongo.errors import PyMongoError
from urllib2 import HTTPError, URLError
import datetime
import time

# name of iqiyi site
SOURCE_NAME = 'iqiyi'

class IQIYICrawler(object):
    '''
    Crawler for iqiyi movie (http://www.iqiyi.com/dianying/).
    '''

    logger = get_logger('IQIYICrawler', 'iqiyi_crawler.log')

    def __init__(self, sleep_time):
        self.sleep_time = sleep_time
        self.__total_movies_crawled = 0

    def start_crawl(self):
        while True:
            IQIYICrawler.logger.info('==========Start to crawl iqiyi movies==========')
            self.__start_crawl()
            IQIYICrawler.logger.info('==========Finish crawling iqiyi movies=========')
            IQIYICrawler.logger.info('==========Totally movies(%s)===================' % self.__total_movies_crawled)

    def __start_crawl(self):
        '''
        Crawl 'movie list page' with URL pattern <http://list.iqiyi.com/www/1/------------2-1-%s-1---.html>
        '''

        self.__total_movies_crawled = 0
        page_index = 1
        while True:
            try:
                movie_list_page_url = 'http://list.iqiyi.com/www/1/------------2-1-%s-1---.html' % page_index
                page_index += 1
                response = request.get(movie_list_page_url, retry_interval=self.sleep_time)
                response_text = response.read()
                IQIYICrawler.logger.debug('Crawled <%s>' % movie_list_page_url)
                if self.sleep_time > 0:
                    time.sleep(self.sleep_time)

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
                        movie_year, movie_summary = self.parse_playing_page(playing_page_url)
                        if not movie_year:
                            IQIYICrawler.logger.warning('Movie year not found on playing page <%s>. Please check whether the xpath has changed' % playing_page_url)
                        if not movie_summary:
                            IQIYICrawler.logger.warning('Movie summary not found on playing page <%s>. Please check whether the xpath has changed' % playing_page_url)
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
                        intro_page_url = movie_intro_elements[0].attrib['href']
                    else:
                        IQIYICrawler.logger.warning('Introduction page URL not found on movie list page <%s>. Please check whether the xpath has changed' % movie_list_page_url)
                        continue

                    #----------get movie title on introduction page----------
                    try:
                        movie_title = self.parse_intro_page(intro_page_url)
                        if not movie_title:
                            IQIYICrawler.logger.warning('Movie title not found on introduction page <%s>. Please check whether the xpath has changed' % intro_page_url)
                            continue  # skip this movie
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
                        movie_obj = {'source': SOURCE_NAME, 'title': movie_title, 'link': playing_page_url, 'last_updated': datetime.datetime.utcnow()}
                        query = {'source': SOURCE_NAME, 'title': movie_title}
                        if movie_year:
                            movie_obj['year'] = movie_year
                            query['year'] = movie_year
                        if movie_definition:
                            movie_obj['definition'] = movie_definition
                            query['definition'] = movie_definition
                        if movie_summary:
                            movie_obj['summary'] = movie_summary

                        movie_source_collection.update(query, movie_obj, upsert=True)

                        self.__total_movies_crawled += 1
                        IQIYICrawler.logger.info('Crawled movie #%s <%s %s %s>' % (self.__total_movies_crawled, movie_year, movie_title, movie_definition))

                    except PyMongoError, e:
                        IQIYICrawler.logger.error('Mongodb error <%s %s>' % (e, playing_page_url))
                        continue
                    #--------------------------------------------------------

            except HTTPError, e:
                IQIYICrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (movie_list_page_url, e.code, e.msg))
            except URLError, e:
                IQIYICrawler.logger.error('Failed to reach server <%s %s>' % (movie_list_page_url, e.reason))
            except Exception, e:
                IQIYICrawler.logger.error('%s <%s>' % (e, movie_list_page_url))

    def parse_playing_page(self, playing_page_url):
        '''
        Parse playing page.
        '''

        response = request.get(playing_page_url, retry_interval=self.sleep_time)
        response_text = response.read()
        IQIYICrawler.logger.debug('Crawled <%s>' % playing_page_url)
        if self.sleep_time > 0:
            time.sleep(self.sleep_time)

        html_element = fromstring(response_text)
        movie_year_elements = html_element.xpath('/html/body/div/div/h1[@id="navbar"]/span/a')
        movie_summary_elements = html_element.xpath('/html/body//div[@class="wenzi"]/p[@class="wenzi1"]')

        return (movie_year_elements[0].text.strip() if movie_year_elements and movie_year_elements[0].text else None,
                movie_summary_elements[0].text.strip() if movie_summary_elements and movie_summary_elements[0].text else None)

    def parse_intro_page(self, intro_page_url):
        '''
        Parse introduction page.
        '''

        response = request.get(intro_page_url, retry_interval=self.sleep_time)
        response_text = response.read()
        IQIYICrawler.logger.debug('Crawled <%s>' % intro_page_url)
        if self.sleep_time > 0:
            time.sleep(self.sleep_time)

        html_element = fromstring(response_text.decode('utf-8', 'ignore'))
        movie_title_elements = html_element.xpath('/html/body/div/div/div/div/div/div[@class="prof-title"]/h1')

        return movie_title_elements[0].text.strip() if movie_title_elements and movie_title_elements[0].text else None

if __name__ == '__main__':
    ic = IQIYICrawler(1)
    ic.start_crawl()
