'''
Created on Nov 26, 2012

@author: Fang Jiaguo
'''
from sets import Set
from urlparse import urlparse
from web_crawler import WebCrawler

class DoubanCrawler(WebCrawler):
    '''
    Crawler for douban move site (http://movie.douban.com/).
    '''

    def __init__(self, start_urls=None, allowed_domains=None, depth= -1, sleep_time=0):
        super(DoubanCrawler, self).__init__(start_urls, allowed_domains, depth, sleep_time)
        self.__crawled_movie_ids = Set()

    def parse(self, response):
        link_elements = response.xpath('//a[@href]')
        for link_element in link_elements:
            url = link_element.attrib['href']
            if url.startswith('http://movie.douban.com/subject'):
                paths = [x for x in urlparse(url).path.split('/') if x]
                if len(paths) >= 2 and paths[0] == 'subject' and paths[1].isdigit() and paths[1] not in self.__crawled_movie_ids:
                    self.__crawled_movie_ids.add(paths[1])
                    print len(self.__crawled_movie_ids), url, paths[1]

if __name__ == '__main__':
    c = DoubanCrawler(['http://movie.douban.com/tag'], ['movie.douban.com'], 2, 6)
    c.start_crawl()
