'''
Created on Nov 26, 2012

@author: Fang Jiaguo
'''
from mongodb import movies_store_collection
from pymongo.errors import PyMongoError
from sets import Set
from urllib2 import HTTPError, URLError
from urlparse import urlparse
from utils import request
from utils.log import log
from web_crawler import WebCrawler
import datetime
import json
import time

# douban api key
apikey = '05bc4743e8f8808a1134d5cbbae9819e'

class DoubanCrawler(WebCrawler):
    '''
    Crawler for douban move site (http://movie.douban.com/).
    '''

    def __init__(self, start_urls, allowed_domains=None, query_params=None, sleep_time=5):
        super(DoubanCrawler, self).__init__(start_urls, allowed_domains, query_params, sleep_time)
        self.__sleep_time = sleep_time
        self.__crawled_movie_ids = Set()
        self.__logger = log.get_child_logger('DoubanCrawler')

    def start_crawl(self):
        self.__logger.info('Start to crawl douban movie site')
        super(DoubanCrawler, self).start_crawl()
        self.__logger.info('Finish crawling douban movie site')
        self.__logger.info('Total douban movies crawled: %s' % len(self.__crawled_movie_ids))

    def parse(self, html_element):
        # Extract all links in the document.
        link_elements = html_element.xpath('//a[@href]')
        for link_element in link_elements:
            url = link_element.attrib['href']
            # The URL must be link 'http://movie.douban.com/subject/12345678/blabla'
            if url.startswith('http://movie.douban.com/subject'):
                paths = [x for x in urlparse(url).path.split('/') if x]
                if len(paths) >= 2 and paths[0] == 'subject' and paths[1].isdigit() and paths[1] not in self.__crawled_movie_ids:
                    try:
                        api_url = 'https://api.douban.com/v2/movie/%s' % paths[1]
                        response = request.get(api_url, params={'apikey': apikey}, retry_interval=self.__sleep_time)
                        response_text = response.read().decode('utf-8', 'ignore')
                        if self.__sleep_time > 0:
                            time.sleep(self.__sleep_time)

                        movie_obj = json.loads(response_text)
                        movie_year = movie_obj['attrs']['year'][0] if 'attrs' in movie_obj and 'year' in movie_obj['attrs'] and movie_obj['attrs']['year'] else 'Unknown'
                        movie_title = movie_obj['title'] if 'title' in movie_obj else 'Unknown'
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
                        movies_store_collection.update({'year': movie_year, 'year': movie_title}, {'$set': new_movie_obj}, True)

                        self.__crawled_movie_ids.add(paths[1])

                        self.__logger.info('Crawled movie #%s "%s"' % (len(self.__crawled_movie_ids), movie_title))

                    except HTTPError, e:
                        self.__logger.error('Server cannot fulfill the request <%s HTTP Error %s: %s>' % (api_url, e.code, e.msg))
                    except URLError, e:
                        self.__logger.error('Failed to reach server <%s Reason: %s>' % (api_url, e.reason))
                    except PyMongoError, e:
                        self.__logger.error('Mongodb error: %s <%s>' % (e, api_url))
                    except Exception, e:
                        self.__logger.error('Unknow exception: %s <%s>' % (e, api_url))

if __name__ == '__main__':
    dc = DoubanCrawler(start_urls=['http://movie.douban.com/tag/'], allowed_domains=['movie.douban.com'],
                       query_params={'apikey': apikey}, sleep_time=1.5)
    dc.start_crawl()
