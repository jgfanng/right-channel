# -*- coding: utf-8 -*-

'''
Created on Nov 26, 2012

@author: Fang Jiaguo
'''
from crawlers.utils import request
from crawlers.utils.limited_caller import LimitedCaller
from crawlers.utils.log import get_logger
from crawlers.utils.mongodb import movies_store_collection
from crawlers.utils.title_simplifier import simplify
from lxml.html import fromstring
from pymongo.errors import PyMongoError
from sets import Set
from urllib2 import HTTPError, URLError
from urlparse import urldefrag
import datetime
import json
import md5
import re

# douban api key
APIKEY = '05bc4743e8f8808a1134d5cbbae9819e'
# douban movie link regular expression
MOVIE_LINK_RE = re.compile('^http://movie\.douban\.com/subject/[0-9]+/?$')

class DoubanCrawler():
    '''
    Crawler for douban move site (http://movie.douban.com/).
    '''

    logger = get_logger('DoubanCrawler', 'douban_crawler.log')

    def __init__(self, start_urls, allowed_url_res=None, additional_qs=None):
        # A list of URLs where the crawler will begin to crawl from.
        self.__start_urls = start_urls
        # An optional list of strings containing URL regex that this crawler is allowed to crawl.
        self.__allowed_url_res = [re.compile(item) for item in allowed_url_res]
        # Query string parameters when sending a request.
        self.__additional_qs = additional_qs
        # A list of URLs the crawler will crawl.
        self.__uncrawled_urls = []
        # Distinct URLs (md5) the crawler has crawled.
        self.__crawled_urls = Set()
        # Total movies crawled.
        self.__total_movies_crawled = 0
        # Throttle douban api call under 40 in 60s.
        self.__douban_call = LimitedCaller(request.get, 60, 40)

    def start_crawl(self):
        DoubanCrawler.logger.info('==========Start to crawl douban movies==========')
        self.__start_crawl()
        DoubanCrawler.logger.info('==========Finish crawling douban movies==========')
        DoubanCrawler.logger.info('==========Totally crawled %s movies==========' % len(self.__crawled_urls))

    def __start_crawl(self):
        # Push start URLs as seeds.
        for start_url in self.__start_urls:
            url_md5 = md5.new(start_url.encode('utf-8')).digest()
            if url_md5 not in self.__crawled_urls:
                self.__crawled_urls.add(url_md5)
                self.__uncrawled_urls.append(start_url)

        while self.__uncrawled_urls:
            try:
                # Pop out the first URL.
                url_to_crawl = self.__uncrawled_urls.pop(0)
                response = self.__douban_call(url_to_crawl.encode('utf-8'), additional_qs=self.__additional_qs)
                response_text = response.read()
                DoubanCrawler.logger.debug('Crawled <%s>' % url_to_crawl)

                html_element = fromstring(response_text)
                html_element.make_links_absolute(url_to_crawl)
                link_elements = html_element.xpath('//a[@href]')
                for link_element in link_elements:
                    url_in_page = link_element.attrib['href']
                    # Remove fragment identifier.
                    url_in_page = urldefrag(url_in_page)[0]
                    # Add the URL if its domain is allowed, and has not been crawled.
                    if self.__url_is_allowed(url_in_page):
                        url_md5 = md5.new(url_in_page.encode('utf-8')).digest()
                        if url_md5 not in self.__crawled_urls:
                            self.__crawled_urls.add(url_md5)
                            self.__uncrawled_urls.append(url_in_page)
                            # Validate movie link using predefined regex.
                            if MOVIE_LINK_RE.match(url_in_page):
                                movie_id = url_in_page[len('http://movie.douban.com/subject/'):-1] if url_in_page.endswith('/') else url_in_page[len('http://movie.douban.com/subject/'):]

                                #----------get movie info through douban api-------------
                                try:
                                    movie_info = self.__get_movie_info(movie_id)
                                except HTTPError, e:
                                    DoubanCrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (movie_id, e.code, e.msg))
                                    continue
                                except URLError, e:
                                    DoubanCrawler.logger.error('Failed to reach server <%s %s>' % (movie_id, e.reason))
                                    continue
                                except Exception, e:
                                    DoubanCrawler.logger.error('%s <%s>' % (e, movie_id))
                                    continue

                                #----------Save to Mongodb-------------------------------
                                try:
                                    if 'simp_titles' in movie_info:
                                        simp_titles = movie_info.pop('simp_titles')
                                        movies_store_collection.update({'id': movie_id}, {'$set': movie_info, '$addToSet': {'simp_titles': {'$each': simp_titles}}}, upsert=True)
                                    else:
                                        movies_store_collection.update({'id': movie_id}, {'$set': movie_info}, upsert=True)
                                except PyMongoError, e:
                                    DoubanCrawler.logger.error('%s <%s %s>' % (e, movie_info['year'] if 'year' in movie_info else None, movie_info['title'] if 'title' in movie_info else None))
                                    continue
                                #--------------------------------------------------------

                                self.__total_movies_crawled += 1
                                DoubanCrawler.logger.info('Crawled movie #%s <%s %s> C(%s) U(%s)' % (self.__total_movies_crawled, movie_info['year'] if 'year' in movie_info else None, movie_info['title'] if 'title' in movie_info else None, len(self.__crawled_urls), len(self.__uncrawled_urls)))

            except HTTPError, e:
                DoubanCrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (url_to_crawl, e.code, e.msg))
            except URLError, e:
                DoubanCrawler.logger.error('Failed to reach server <%s %s>' % (url_to_crawl, e.reason))
            except Exception, e:
                DoubanCrawler.logger.error('%s <%s>' % (e, url_to_crawl))

    def __get_movie_info(self, movie_id):
        '''
        Get movie info through douban api
        '''

        api_url = 'https://api.douban.com/v2/movie/%s' % movie_id
        response = self.__douban_call(api_url.encode('utf-8'), additional_qs=self.__additional_qs)
        response_text = response.read()

        movie_obj = json.loads(response_text)
        new_movie_obj = {'id': movie_id}
        if 'attrs' in movie_obj and 'year' in movie_obj['attrs'] and movie_obj['attrs']['year'] and movie_obj['attrs']['year'][0]:
            new_movie_obj['year'] = movie_obj['attrs']['year'][0].strip()
        if 'title' in movie_obj and movie_obj['title']:
            new_movie_obj['title'] = movie_obj['title'].strip()
            # get simplified title
            simp_title = simplify(new_movie_obj['title'])
            if simp_title != new_movie_obj['title']:
                new_movie_obj['simp_titles'] = [simp_title]
        if 'alt_title' in movie_obj and movie_obj['alt_title']:
            alt_titles = [item.strip() for item in movie_obj['alt_title'].split(' / ')]
            if alt_titles:
                new_movie_obj['alt_titles'] = alt_titles
                for item in new_movie_obj['alt_titles']:
                    # get simplified title
                    simp_title = simplify(item)
                    if simp_title not in new_movie_obj['alt_titles']:
                        if 'simp_titles' not in new_movie_obj:
                            new_movie_obj['simp_titles'] = []
                        if simp_title not in new_movie_obj['simp_titles']:
                            new_movie_obj['simp_titles'].append(simp_title)
        if 'attrs' in movie_obj and 'director' in movie_obj['attrs'] and movie_obj['attrs']['director']:
            new_movie_obj['directors'] = movie_obj['attrs']['director']
        if 'attrs' in movie_obj and 'writer' in movie_obj['attrs'] and movie_obj['attrs']['writer']:
            new_movie_obj['writers'] = movie_obj['attrs']['writer']
        if 'attrs' in movie_obj and 'cast' in movie_obj['attrs'] and movie_obj['attrs']['cast']:
            new_movie_obj['casts'] = movie_obj['attrs']['cast']
        if 'attrs' in movie_obj and 'episodes' in movie_obj['attrs'] and movie_obj['attrs']['episodes'] and movie_obj['attrs']['episodes'][0]:
            new_movie_obj['episodes'] = int(movie_obj['attrs']['episodes'][0])
        if 'attrs' in movie_obj and 'movie_type' in movie_obj['attrs'] and movie_obj['attrs']['movie_type']:
            new_movie_obj['types'] = movie_obj['attrs']['movie_type']
        if 'attrs' in movie_obj and 'country' in movie_obj['attrs'] and movie_obj['attrs']['country']:
            new_movie_obj['countries'] = movie_obj['attrs']['country']
        if 'attrs' in movie_obj and 'language' in movie_obj['attrs'] and movie_obj['attrs']['language']:
            new_movie_obj['languages'] = movie_obj['attrs']['language']
        if 'attrs' in movie_obj and 'pubdate' in movie_obj['attrs'] and movie_obj['attrs']['pubdate']:
            new_movie_obj['pubdates'] = movie_obj['attrs']['pubdate']
        if 'attrs' in movie_obj and 'movie_duration' in movie_obj['attrs'] and movie_obj['attrs']['movie_duration']:
            new_movie_obj['durations'] = movie_obj['attrs']['movie_duration']
        if 'image' in movie_obj and movie_obj['image']:
            new_movie_obj['image'] = movie_obj['image']
        if 'summary' in movie_obj and movie_obj['summary']:
            new_movie_obj['summary'] = movie_obj['summary']
        new_movie_obj['douban'] = {'last_updated': datetime.datetime.utcnow()}
        if 'rating' in movie_obj and 'average' in movie_obj['rating'] and movie_obj['rating']['average']:
            new_movie_obj['douban']['score'] = float(movie_obj['rating']['average'])
        if 'alt' in movie_obj and movie_obj['alt']:
            new_movie_obj['douban']['link'] = movie_obj['alt']

        return new_movie_obj

    def __url_is_allowed(self, url):
        # Return True if URL pattern is allowed, otherwise False.
        if not self.__allowed_url_res:
            return True

        for re in self.__allowed_url_res:
            if re.match(url):
                return True

        return False
