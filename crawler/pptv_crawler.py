'''
Created on Nov 25, 2012

@author: Fang Jiaguo
'''

from lxml.html import fromstring
from pymongo.connection import Connection
import datetime
import time
import urllib2

class PPTVCrawler:
    '''
    Crawler for PPTV move site (http://www.pptv.com/).
    '''

    def __init__(self, sleep_time):
        self.__sleep_time = sleep_time
        self.__connection = Connection()
        self.__db = self.__connection['videocabindb']
        self.__collection = self.__db['movies']

    def crawl(self):
        page_index = 1
        movie_index = 1
        while True:
            request = urllib2.Request('http://list.pptv.com/sort_list/1---------%s.html' % page_index)
            request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
            response = urllib2.urlopen(request)
#            response = urllib2.urlopen('http://list.pptv.com/sort_list/1---------%s.html' % page_index)
            plain_text = response.read().decode('utf-8', 'ignore')
            print "Parsing", 'http://list.pptv.com/sort_list/1---------%s.html' % page_index
            html_element = fromstring(plain_text)
            page_index += 1
#            print plain_text

            movie_elements = html_element.xpath('/html/body/div/div/div/div[@class="bd"]/ul/li/p[@class="txt"]/a')
            if len(movie_elements) == 0:
                break

            for movie_element in movie_elements:
                if not movie_element.attrib['href'].startswith('http://v.pptv.com/show'):
                    print movie_index, movie_element.text, 'Bad format 1 ====================>', movie_element.attrib['href']
                    movie_index += 1
                    continue

                time.sleep(self.__sleep_time)

                response = urllib2.urlopen(movie_element.attrib['href'])
                plain_text = response.read().decode('utf-8', 'ignore')
                print "Parsing", movie_element.attrib['href']
                html_element = None
                try:
                    html_element = fromstring(plain_text)
                except Exception, e:
                    print e
                    movie_index += 1
                    continue
                movie_title_elements = html_element.xpath('/html/body/div/div/div[@class="sbox showinfo"]/div[@class="bd"]/ul/li[1]/h3/a')
                if len(movie_title_elements) == 0:
                    print movie_index, movie_element.text, 'Bad format 2 ====================>', movie_element.attrib['href']
                    movie_index += 1
                    continue

                year = movie_title_elements[0].tail[1:-1]

                time.sleep(self.__sleep_time)

                response = None
                try:
                    response = urllib2.urlopen(movie_title_elements[0].attrib['href'])
                except:
                    movie_index += 1
                    continue
                plain_text = response.read().decode('utf-8', 'ignore')
                print "Parsing", movie_title_elements[0].attrib['href']
                html_element = None
                try:
                    html_element = fromstring(plain_text)
                except Exception, e:
                    print e
                    movie_index += 1
                    continue
                actual_movie_title_elements = html_element.xpath('/html/body/div/span[@class="crumb_current"]')
                if len(actual_movie_title_elements) == 0:
                    print movie_index, movie_element.text, 'Bad format 3 ====================>', movie_title_elements[0].attrib['href']
                    movie_index += 1
                    continue
#                movie_cast_elements = movie_element.xpath('./p[@class="p_actor"]/a')
#                movie_image_element = movie_element.xpath('./p[@class="pic"]/a/img')[0]
                # TODO: If original url has been changed, the 'play_times' should be set to ZERO.
                self.__collection.update({'title': actual_movie_title_elements[0].text.strip(), 'year': int(year)},
                                         {'$set': {'pptv.link': movie_element.attrib['href'], 'pptv.last_updated': datetime.datetime.utcnow()}, '$inc': {'pptv.play_times': 0}},
                                         True)

                print movie_index, actual_movie_title_elements[0].text.strip(), year, movie_element.attrib['href']
#                for movie_cast_element in movie_cast_elements:
#                    print movie_cast_element.text,
#                print movie_image_element.attrib['src']
                movie_index += 1

            time.sleep(self.__sleep_time)

if __name__ == '__main__':
    c = PPTVCrawler(2)
    c.crawl()
