'''
Created on Nov 25, 2012

@author: Fang Jiaguo
'''

from crawler_base import CrawlerBase
from lxml.html import fromstring
from pymongo.connection import Connection
import time
import urllib2

class PPTVCrawler(CrawlerBase):
    '''
    Crawler for PPTV move site (http://www.pptv.com/).
    '''

    def __init__(self, sleep_time):
        self.__sleep_time = sleep_time
        self.__connection = Connection()
        self.__db = self.__connection['videocabindb']
        self.__collection = self.__db['movies']

    def crawl(self):
        page_index = 172
        movie_index = 1
        while True:
            response = urllib2.urlopen('http://list.pptv.com/sort_list/1---------%s.html' % page_index)
            page_index += 1

            plain_text = response.read().decode('utf-8', 'ignore')
            html_element = fromstring(plain_text)

            movie_elements = html_element.xpath('/html/body/div/div/div/div[@class="bd"]/ul/li')
            if len(movie_elements) == 0:
                break

            for movie_element in movie_elements:
                movie_title_element = movie_element.xpath('./p[@class="txt"]/a')[0]
                movie_cast_elements = movie_element.xpath('./p[@class="p_actor"]/a')
                movie_image_element = movie_element.xpath('./p[@class="pic"]/a/img')[0]
                self.__collection.update({'title': movie_title_element.text}, {'$set': {'pptv.link': movie_title_element.attrib['href']}, '$inc': {'pptv.play_times': 0}}, True)

                print movie_index, movie_title_element.text, movie_title_element.attrib['href'],
                for movie_cast_element in movie_cast_elements:
                    print movie_cast_element.text,
                print movie_image_element.attrib['src']
                movie_index += 1

            time.sleep(self.__sleep_time)

if __name__ == '__main__':
    c = PPTVCrawler(5)
    c.crawl()
