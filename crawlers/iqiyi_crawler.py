# -*- coding: utf-8 -*-

'''
Created on Dec 7, 2012

@author: Fang Jiaguo
'''
from Queue import Queue
from crawlers.utils import request
from crawlers.utils.log import get_logger
from crawlers.utils.mongodb import movie_store_collection
from difflib import SequenceMatcher
from lxml.html import fromstring
from pymongo.errors import PyMongoError
from threading import Thread
from urllib2 import HTTPError, URLError
import datetime
import time

class IQIYICrawler(object):
    '''
    Crawler for iqiyi movie (http://www.iqiyi.com/dianying/).
    '''

    logger = get_logger('IQIYICrawler', 'iqiyi_crawler.log')

    def __init__(self, sleep_time):
        self.sleep_time = sleep_time
        self.__unmatched_queue = Queue()
        self.__total_movies_crawled = 0

    def start_crawl(self):
        # this thread is used to manually match movies which are not indexed by mongodb
        matcher = Thread(target=self.__match_manually)
        matcher.start()
        # start to crawl iqiyi
        while True:
            IQIYICrawler.logger.info('==========Start to crawl iqiyi movies==========')
            self.__start_crawl()
            IQIYICrawler.logger.info('==========Finish crawling iqiyi movies=========')
            IQIYICrawler.logger.info('==========Total movies: %s===================' % self.__total_movies_crawled)

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
                        movie_year = self.parse_playing_page(playing_page_url)
                        if not movie_year:
                            IQIYICrawler.logger.warning('Movie year not found on playing page <%s>. Please check whether the xpath has changed' % playing_page_url)
                    except HTTPError, e:
                        IQIYICrawler.logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (playing_page_url, e.code, e.msg))
                        continue
                    except URLError, e:
                        IQIYICrawler.logger.error('Failed to reach server <%s> <%s>' % (playing_page_url, e.reason))
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
                        IQIYICrawler.logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (intro_page_url, e.code, e.msg))
                        continue
                    except URLError, e:
                        IQIYICrawler.logger.error('Failed to reach server <%s> <%s>' % (intro_page_url, e.reason))
                        continue
                    except Exception, e:
                        IQIYICrawler.logger.error('%s <%s>' % (e, intro_page_url))
                        continue

                    #----------get movie definition--------------------------
                    movie_definition_elements = movie_element.xpath('./a/span[@class="cqBg"]')
                    movie_definition = u'超清' if movie_definition_elements else u'一般'

                    self.__total_movies_crawled += 1
                    IQIYICrawler.logger.info('Crawled movie #%s <%s> <%s> <%s>' % (self.__total_movies_crawled, movie_year, movie_title, movie_definition))

                    #----------Save to Mongodb-------------------------------
                    try:
                        result = movie_store_collection.find_and_modify(query={'year': movie_year, '$or': [{'title': movie_title}, {'alt_titles': movie_title}]},  # Caution: if 'movie_year' is None, mongodb will return records with no 'year' field or its value is 'null'
                                                                        update={'$set': {'iqiyi.title': movie_title, 'iqiyi.similarity': 1.0, 'iqiyi.link': playing_page_url, 'iqiyi.definition': movie_definition, 'iqiyi.last_updated': datetime.datetime.utcnow()}, '$inc': {'iqiyi.play_times': 0}},  # Caution: if 'play_times' does not exist, mongodb will automatically set its value to 0
                                                                        fields={'_id': 1})
                        if result:
                            IQIYICrawler.logger.info('Find a match with douban <%s>' % movie_title)
                        else:
                            self.__unmatched_queue.put((movie_year, movie_title, playing_page_url, movie_definition))
                            IQIYICrawler.logger.info('Cannot find a match with douban <%s>' % movie_title)

                    except PyMongoError, e:
                        IQIYICrawler.logger.error('Mongodb error <%s> <%s>' % (e, playing_page_url))
                        continue
                    #--------------------------------------------------------

            except HTTPError, e:
                IQIYICrawler.logger.error('Server cannot fulfill the request <%s> <%s> <%s>' % (movie_list_page_url, e.code, e.msg))
            except URLError, e:
                IQIYICrawler.logger.error('Failed to reach server <%s> <%s>' % (movie_list_page_url, e.reason))
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

        return movie_year_elements[0].text.strip() if movie_year_elements and movie_year_elements[0].text else None

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

    def __match_manually(self):
        '''
        Traverse mongodb and manually match movies.
        '''

        while True:
            try:
                movie_year, movie_title, playing_page_url, movie_definition = self.__unmatched_queue.get()
                max_score = 0.0
                similar_movie = None
                for movie_info in movie_store_collection.find(fields={'_id': 0, 'id': 1, 'year': 1, 'title': 1, 'alt_titles': 1}, snapshot=True):
                    titles = []
                    if 'title' in movie_info:
                        titles.append(movie_info['title'])
                    if 'alt_titles' in movie_info:
                        titles.extend(movie_info['alt_titles'])

                    for title in titles:
                        m = SequenceMatcher(None, title, movie_title, autojunk=False)
                        score = m.ratio()
                        if (score > max_score) or (score == max_score and movie_year == movie_info.get('year')):
                            max_score = score
                            similar_movie = movie_info

                if max_score > 0.0 and similar_movie:
                    movie_store_collection.update({'id': similar_movie['id']},
                                                  {'$set': {'sources.iqiyi.title': movie_title, 'sources.iqiyi.similarity': max_score, 'sources.iqiyi.link': playing_page_url,
                                                            'sources.iqiyi.definition': movie_definition, 'sources.iqiyi.last_updated': datetime.datetime.utcnow()}})
                    IQIYICrawler.logger.info('Find a similar movie in douban <%s> <%s> <%s>' % (movie_title, similar_movie.get('title'), max_score))
                else:
                    IQIYICrawler.logger.warning('Cannot find any similar movie with douban <%s>' % movie_title)

            except PyMongoError, e:
                IQIYICrawler.logger.error('Mongodb error <%s> when manually matching movie <%s>' % (e, movie_title))
            except Exception, e:
                IQIYICrawler.logger.error('%s <%s>' % (e, movie_title))

if __name__ == '__main__':
    ic = IQIYICrawler(1)
    ic.start_crawl()
