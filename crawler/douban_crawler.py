'''
Created on Nov 26, 2012

@author: Fang Jiaguo
'''
from lxml.html import fromstring
import time
import urllib2

class DoubanCrawler:
    '''
    Crawler for douban move site (http://www.douban.com/).
    '''

    def __init__(self, sleep_time):
        self.__sleep_time = sleep_time

    def crawl(self):
        year = 2012
        movie_index = 0
        while True:
            response = urllib2.urlopen('http://movie.douban.com/tag/%s?start=%s' % (year, movie_index))

            plain_text = response.read().decode('utf-8', 'ignore')
            html_element = fromstring(plain_text)

            movie_elements = html_element.xpath('/html/body/div/div[@id="content"]/div/div[@class="article"]/div[@id="subject_list"]/table/tr[@class="item"]/td[2]/div[1]/a')
            if len(movie_elements) == 0:
                break

            for movie_element in movie_elements:
                print movie_index, movie_element.attrib['href'], movie_element.text_content()
                movie_index += 1

            time.sleep(self.__sleep_time)

if __name__ == '__main__':
    c = DoubanCrawler(6)
    c.crawl()
