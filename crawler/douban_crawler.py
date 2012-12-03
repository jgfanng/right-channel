'''
Created on Nov 26, 2012

@author: Fang Jiaguo
'''
from datetime import datetime
from mongodb import movies_store_collection
from sets import Set
from urlparse import urlparse
from web_crawler import WebCrawler
import json
import time
import urllib2

class DoubanCrawler(WebCrawler):
    '''
    Crawler for douban move site (http://movie.douban.com/).
    '''

    def __init__(self, start_urls, allowed_domains=None, depth= -1, sleep_time=1):
        super(DoubanCrawler, self).__init__(start_urls, allowed_domains, depth, sleep_time)
        self.__sleep_time = sleep_time
        self.__crawled_movie_ids = Set()

    def parse(self, response):
        link_elements = response.xpath('//a[@href]')
        for link_element in link_elements:
            url = link_element.attrib['href']
            if url.startswith('http://movie.douban.com/subject'):
                paths = [x for x in urlparse(url).path.split('/') if x]
                if len(paths) >= 2 and paths[0] == 'subject' and paths[1].isdigit() and paths[1] not in self.__crawled_movie_ids:
                    self.__crawled_movie_ids.add(paths[1])
                    request = urllib2.urlopen('https://api.douban.com/v2/movie/%s?apikey=%s' % (paths[1], '05bc4743e8f8808a1134d5cbbae9819e'))
                    response_text = request.read().decode('utf-8', 'ignore')
                    movie_obj = json.loads(response_text)
                    try:
                        movies_store_collection.update({'title': movie_obj['title'], 'year': int(movie_obj['attrs']['year'][0]) if 'attrs' in movie_obj and 'year' in movie_obj['attrs'] and movie_obj['attrs']['year'] else -1},
                                                 {'$set': {'douban': {'directors': movie_obj['attrs']['director'] if 'attrs' in movie_obj and 'director' in movie_obj['attrs'] else [],
                                                                      'writers': movie_obj['attrs']['writer'] if 'attrs' in movie_obj and 'writer' in movie_obj['attrs'] else [],
                                                                      'casts': movie_obj['attrs']['cast'] if 'attrs' in movie_obj and 'cast' in movie_obj['attrs'] else [],
                                                                      'types': movie_obj['attrs']['movie_type'] if 'attrs' in movie_obj and 'movie_type' in movie_obj['attrs'] else [],
                                                                      'countries': movie_obj['attrs']['country'] if 'attrs' in movie_obj and 'country' in movie_obj['attrs'] else [],
                                                                      'languages': movie_obj['attrs']['language'] if 'attrs' in movie_obj and 'language' in movie_obj['attrs'] else [],
                                                                      'pubdates': movie_obj['attrs']['pubdate'] if 'attrs' in movie_obj and 'pubdate' in movie_obj['attrs'] else [],
                                                                      'durations': movie_obj['attrs']['movie_duration'] if 'attrs' in movie_obj and 'movie_duration' in movie_obj['attrs'] else [],
                                                                      'alt_title': movie_obj['alt_title'] if 'alt_title' in movie_obj else '',
                                                                      'summary': movie_obj['summary'] if 'summary' in movie_obj else '',
                                                                      'score': float(movie_obj['rating']['average']) if 'rating' in movie_obj and 'average' in movie_obj['rating'] else -1,
                                                                      'link': movie_obj['alt'] if 'alt' in movie_obj else '',
                                                                      'image': movie_obj['image'] if 'image' in movie_obj else '',
                                                                      'tags': [item['name'] for item in movie_obj['tags']] if 'tags' in movie_obj else [],
                                                                      'last_updated': datetime.utcnow()}}},
                                                 True)
                    except:
                        print movie_obj
                    print len(self.__crawled_movie_ids), movie_obj['title']
                    time.sleep(self.__sleep_time)

if __name__ == '__main__':
    print datetime.now()
    c = DoubanCrawler(['http://movie.douban.com/tag'], ['movie.douban.com'], 2, 1.5)
    c.start_crawl()
    print datetime.now()
