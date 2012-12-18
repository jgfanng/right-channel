# -*- coding: utf-8 -*-

'''
Created on Nov 25, 2012

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

# name of pptv site
SOURCE_NAME = 'pptv'

class PPTVCrawler(object):
    '''
    Crawler for pptv move (http://movie.pptv.com/).
    '''

    logger = get_logger('PPTVCrawler', 'pptv_crawler.log')

    def __init__(self, sleep_time):
        self.sleep_time = sleep_time
        self.__total_movies_crawled = 0

    def start_crawl(self):
        while True:
            PPTVCrawler.logger.info('==========Start to crawl pptv movies==========')
            self.__start_crawl()
            PPTVCrawler.logger.info('==========Finish crawling pptv movies=========')
            PPTVCrawler.logger.info('==========Totally movies(%s)==================' % self.__total_movies_crawled)

    def __start_crawl(self):
        '''
        Crawl 'movie list page' with URL pattern <http://list.pptv.com/sort_list/1---------%s.html>
        '''

        self.__total_movies_crawled = 0
        page_index = 1
        while True:
            try:
                movie_list_page_url = 'http://list.pptv.com/sort_list/1---------%s.html' % page_index
                page_index += 1
                response = request.get(movie_list_page_url, retry_interval=self.sleep_time)
                response_text = response.read()
                PPTVCrawler.logger.debug('Crawled <%s>' % movie_list_page_url)
                if self.sleep_time > 0:
                    time.sleep(self.sleep_time)

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
                        movie_year, intro_page_url = self.parse_playing_page(playing_page_url)
                        if not movie_year:
                            PPTVCrawler.logger.warning('Movie year not found on playing page <%s>. Please check whether the xpath has changed' % playing_page_url)
                        if not intro_page_url:
                            PPTVCrawler.logger.warning('Introduction page URL not found on playing page <%s>. Please check whether the xpath has changed' % playing_page_url)
                            continue  # skip this movie
                    except HTTPError, e:
                        PPTVCrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (playing_page_url, e.code, e.msg))
                        continue
                    except URLError, e:
                        PPTVCrawler.logger.error('Failed to reach server <%s %s>' % (playing_page_url, e.reason))
                        continue
                    except Exception, e:
                        PPTVCrawler.logger.error('%s <%s>' % (e, playing_page_url))
                        continue

                    #----------get movie title, definition on introduction page----------
                    try:
                        movie_title, movie_definition, movie_summary = self.parse_intro_page(intro_page_url)
                        if not movie_title:
                            PPTVCrawler.logger.warning('Movie title not found on introduction page <%s>. Please check whether the xpath has changed' % intro_page_url)
                            continue  # skip this movie
                        if not movie_definition:
                            PPTVCrawler.logger.warning('Movie definition not found on introduction page <%s>. Please check whether the xpath has changed' % intro_page_url)
                        if not movie_summary:
                            PPTVCrawler.logger.warning('Movie summary not found on introduction page <%s>. Please check whether the xpath has changed' % intro_page_url)
                    except HTTPError, e:
                        PPTVCrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (intro_page_url, e.code, e.msg))
                        continue
                    except URLError, e:
                        PPTVCrawler.logger.error('Failed to reach server <%s %s>' % (intro_page_url, e.reason))
                        continue
                    except Exception, e:
                        PPTVCrawler.logger.error('%s <%s>' % (e, intro_page_url))
                        continue

                    #--------------------Save to Mongodb---------------------
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
                        PPTVCrawler.logger.info('Crawled movie #%s <%s %s %s>' % (self.__total_movies_crawled, movie_year, movie_title, movie_definition))

                    except PyMongoError, e:
                        PPTVCrawler.logger.error('Mongodb error <%s %s>' % (e, playing_page_url))
                        continue
                    #--------------------------------------------------------

            except HTTPError, e:
                PPTVCrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (movie_list_page_url, e.code, e.msg))
            except URLError, e:
                PPTVCrawler.logger.error('Failed to reach server <%s %s>' % (movie_list_page_url, e.reason))
            except Exception, e:
                PPTVCrawler.logger.error('%s <%s>' % (e, movie_list_page_url))

    def parse_playing_page(self, playing_page_url):
        '''
        Parse playing page.
        '''

        response = request.get(playing_page_url, retry_interval=self.sleep_time)
        response_text = response.read()
        PPTVCrawler.logger.debug('Crawled <%s>' % playing_page_url)
        if self.sleep_time > 0:
            time.sleep(self.sleep_time)

        html_element = fromstring(response_text)
        movie_title_elements = html_element.xpath('/html/body/div/div/div[@class="sbox showinfo"]/div[@class="bd"]/ul/li[1]/h3/a[@href]')
        if movie_title_elements:
            movie_year = movie_title_elements[0].tail
            if movie_year and movie_year.strip() and movie_year.startswith('(') and movie_year.endswith(')'):
                return movie_year[1:-1].strip(), movie_title_elements[0].attrib['href']
            else:
                return None, movie_title_elements[0].attrib['href']
        else:
            return None, None

    def parse_intro_page(self, intro_page_url):
        '''
        Parse introduction page.
        '''

        response = request.get(intro_page_url, retry_interval=self.sleep_time)
        response_text = response.read()
        PPTVCrawler.logger.debug('Crawled <%s>' % intro_page_url)
        if self.sleep_time > 0:
            time.sleep(self.sleep_time)

        html_element = fromstring(response_text)
        movie_title_elements = html_element.xpath('/html/body/div/span[@class="crumb_current"]')
        movie_definition_elements = html_element.xpath('/html/body/div/p[@class="tabs"]/em')
        movie_summary_elements = html_element.xpath('/html/body/div/div/div/ul/li/p[@class="brief_long"]')

        movie_title = movie_title_elements[0].text.strip() if movie_title_elements and movie_title_elements[0].text else None

        movie_definition = None
        for element in movie_definition_elements:
            if element.text.strip().startswith(u'清晰度：'):
                movie_definition = element.text.strip()[len(u'清晰度：'):]
                break

        movie_summary = movie_summary_elements[0].text.strip() if movie_summary_elements and movie_summary_elements[0].text else None

        return (movie_title, movie_definition, movie_summary)

if __name__ == '__main__':
    pc = PPTVCrawler(1)
    pc.start_crawl()
