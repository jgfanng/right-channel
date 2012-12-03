'''
Created on Nov 29, 2012

@author: Fang Jiaguo
'''
from lxml.html import fromstring
from sets import Set
from urlparse import urlparse
import md5
import time
import urllib2

class WebCrawler(object):
    '''
    Base crawler (Binary First Search)
    '''

    def __init__(self, start_urls, allowed_domains=None, depth= -1, sleep_time=1):
        # A list of URLs where the crawler will begin to crawl from.
        self.__start_urls = start_urls
        # An optional list of strings containing domains that this crawler is allowed to crawl.
        self.__allowed_domains = allowed_domains
        # The maximum depth that will be allowed to crawl for any site. If -1, no limit will be imposed.
        self.__depth = depth
        # Sleep some time after crawl a page to avoid Dos attacks.
        self.__sleep_time = sleep_time
        self.__to_crawl_urls = []  # store urls to crawl
        self.__crawled_urls = Set()  # store crawled urls
        self.__current_depth_urls = 0  # url count in the current depth

    def start_crawl(self):
        # push all start urls to crawl
        if self.__depth != 0:
            for start_url in self.__start_urls:
                if self.__url_is_allowed(start_url):
                    url_md5 = md5.new(start_url).digest()
                    if url_md5 not in self.__crawled_urls:
                        self.__crawled_urls.add(url_md5)
                        self.__to_crawl_urls.append(start_url)
                        if self.__depth > 0:
                            self.__current_depth_urls += 1

        while self.__depth != 0 and self.__to_crawl_urls:
            # get first url, then remove it
            to_crawl_url = self.__to_crawl_urls.pop(0)
            request = urllib2.urlopen(to_crawl_url)
            response_text = request.read().decode('utf-8', 'ignore')
            # extract all links
            html_element = fromstring(response_text)
            html_element.make_links_absolute(request.url)
            link_elements = html_element.xpath('//a[@href]')
            for link_element in link_elements:
                url = link_element.attrib['href']
                # if domain is allowed, and url has not been crawled
                if self.__url_is_allowed(url):
                    url_md5 = md5.new(url).digest()
                    if url_md5 not in self.__crawled_urls:
                        self.__crawled_urls.add(url_md5)
                        self.__to_crawl_urls.append(url)
#                        print len(self.__to_crawl_urls), len(self.__crawled_urls), url, link_element.text

            # for throttle
            if self.__sleep_time > 0:
                time.sleep(self.__sleep_time)
            # customized stuff
            self.parse(html_element)

            # decrease url count by 1 in the current depth
            if self.__depth > 0:
                self.__current_depth_urls -= 1
                if self.__current_depth_urls == 0:
                    self.__depth -= 1
                    if self.__depth > 0:
                        self.__current_depth_urls = len(self.__to_crawl_urls)

    def __url_is_allowed(self, url):
        # validate domain name
        hostname = urlparse(url).hostname
        if hostname:
            for domain in self.__allowed_domains:
                if hostname.endswith(domain):
                    return True
        return False

    def parse(self, response):
        pass

if __name__ == '__main__':
    wc = WebCrawler(start_urls=['http://movie.douban.com/tag'], allowed_domains=['movie.douban.com'], depth=2, sleep_time=1.5)
    wc.start_crawl()
