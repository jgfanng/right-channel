# -*- coding: utf-8 -*-

'''
Created on Nov 26, 2012

@author: Fang Jiaguo
'''
from mongodb import movies_store_collection
from pymongo.errors import PyMongoError
from sets import Set
from urllib2 import HTTPError, URLError
from utils import request
from utils.log import log
from web_crawler import WebCrawler
import datetime
import json
import re
import time

# douban api key
apikey = '05bc4743e8f8808a1134d5cbbae9819e'

class DoubanCrawler(WebCrawler):
    '''
    Crawler for douban move site (http://movie.douban.com/).
    '''

    logger = log.get_child_logger('DoubanCrawler')

    def __init__(self, start_urls, allowed_url_res=None, additional_qs=None, sleep_time=5):
        super(DoubanCrawler, self).__init__(start_urls, allowed_url_res, additional_qs, sleep_time)
        self.__sleep_time = sleep_time
        self.__crawled_urls = Set()
        self.__movie_info_re = re.compile('^http://movie\.douban\.com/subject/[0-9a-zA-Z]+/$')

    def start_crawl(self):
        DoubanCrawler.logger.info('Start to crawl douban movie site')
        super(DoubanCrawler, self).start_crawl()
        DoubanCrawler.logger.info('Finish crawling douban movie site')
        DoubanCrawler.logger.info('Total douban movies crawled: %s' % len(self.__crawled_urls))

    def parse(self, html_element):
        # Extract all links in the document, and call douban api to those movie links.
        link_elements = html_element.xpath('//a[@href]')
        for link_element in link_elements:
            url = link_element.attrib['href']
            # The URL must be like 'http://movie.douban.com/subject/blabla...'
            if self.__movie_info_re.match(url):
                movie_id = url[len('http://movie.douban.com/subject/'):-1] if url.endswith('/') else url[len('http://movie.douban.com/subject/'):]
                if movie_id not in self.__crawled_urls:
                    try:
                        api_url = 'https://api.douban.com/v2/movie/%s' % movie_id
                        response = request.get(api_url, additional_qs={'apikey': apikey}, retry_interval=self.__sleep_time)
                        response_text = response.read()  # .decode('utf-8', 'ignore')
                        if self.__sleep_time > 0:
                            time.sleep(self.__sleep_time)

                        movie_obj = json.loads(response_text)
                        movie_year = movie_obj['attrs']['year'][0].strip() if 'attrs' in movie_obj and 'year' in movie_obj['attrs'] and movie_obj['attrs']['year'] else 'Unknown'
                        movie_title = movie_obj['title'].strip() if 'title' in movie_obj else 'Unknown'
                        new_movie_obj = {'year': movie_year, 'title': movie_title}
                        if 'alt_title' in movie_obj:
                            new_movie_obj['alt_titles'] = [x.strip() for x in movie_obj['alt_title'].split('/')]
                        if 'attrs' in movie_obj and 'director' in movie_obj['attrs']:
                            new_movie_obj['directors'] = movie_obj['attrs']['director']
                        if 'attrs' in movie_obj and 'writer' in movie_obj['attrs']:
                            new_movie_obj['writers'] = movie_obj['attrs']['writer']
                        if 'attrs' in movie_obj and 'cast' in movie_obj['attrs']:
                            new_movie_obj['casts'] = movie_obj['attrs']['cast']
                        if 'attrs' in movie_obj and 'movie_type' in movie_obj['attrs']:
                            new_movie_obj['types'] = movie_obj['attrs']['movie_type']
                        if 'attrs' in movie_obj and 'country' in movie_obj['attrs']:
                            new_movie_obj['countries'] = movie_obj['attrs']['country']
                        if 'attrs' in movie_obj and 'language' in movie_obj['attrs']:
                            new_movie_obj['languages'] = movie_obj['attrs']['language']
                        if 'attrs' in movie_obj and 'pubdate' in movie_obj['attrs']:
                            new_movie_obj['pubdates'] = movie_obj['attrs']['pubdate']
                        if 'attrs' in movie_obj and 'movie_duration' in movie_obj['attrs']:
                            new_movie_obj['durations'] = movie_obj['attrs']['movie_duration']
                        if 'image' in movie_obj:
                            new_movie_obj['image'] = movie_obj['image']
                        if 'summary' in movie_obj:
                            new_movie_obj['summary'] = movie_obj['summary']
                        new_movie_obj['douban'] = {'last_updated': datetime.datetime.utcnow()}
                        if 'rating' in movie_obj and 'average' in movie_obj['rating']:
                            new_movie_obj['douban']['score'] = float(movie_obj['rating']['average'])
                        if 'alt' in movie_obj:
                            new_movie_obj['douban']['link'] = movie_obj['alt']
                        movies_store_collection.update({'year': movie_year, 'title': movie_title}, {'$set': new_movie_obj}, True)

                        self.__crawled_urls.add(movie_id)

                        DoubanCrawler.logger.info('Crawled movie #%s <%s %s>' % (len(self.__crawled_urls), movie_year, movie_title))

                    except HTTPError, e:
                        DoubanCrawler.logger.error('Server cannot fulfill the request <%s HTTP Error %s: %s>' % (api_url, e.code, e.msg))
                    except URLError, e:
                        DoubanCrawler.logger.error('Failed to reach server <%s Reason: %s>' % (api_url, e.reason))
                    except PyMongoError, e:
                        DoubanCrawler.logger.error('Mongodb error: %s <%s>' % (e, api_url))
                    except Exception, e:
                        DoubanCrawler.logger.error('Unknow exception: %s <%s>' % (e, api_url))

if __name__ == '__main__':
    dc = DoubanCrawler(start_urls=['http://movie.douban.com/tag/'  # 豆瓣电影标签
                                   ],
                       allowed_url_res=['^http://movie\.douban\.com/tag/',  # 豆瓣电影标签
                                        '^http://movie\.douban\.com/subject/[0-9a-zA-Z]+/{0,1}$'  # 电影主页
                                        ],
                       additional_qs={'apikey': '05bc4743e8f8808a1134d5cbbae9819e'},
                       sleep_time=1.5)
    dc.start_crawl()
