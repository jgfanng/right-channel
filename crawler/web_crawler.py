'''
Created on Nov 29, 2012

@author: Fang Jiaguo
'''
from lxml.html import fromstring
from sets import Set
from urllib2 import HTTPError, URLError
from urlparse import urlparse
from utils import request
from utils.log import log
import md5
import time

class WebCrawler(object):
    '''
    Base crawler (Binary First Search)
    '''

    def __init__(self, start_urls, allowed_domains=None, query_params=None, sleep_time=5):
        # A list of URLs where the crawler will begin to crawl from.
        self.__start_urls = start_urls
        # An optional list of strings containing domains that this crawler is allowed to crawl.
        self.__allowed_domains = allowed_domains
        # Query string parameters when sending a request.
        self.__query_params = query_params
        # Sleep some time after crawl a page for throttle.
        self.__sleep_time = sleep_time
        # A list of URLs the crawler will crawl.
        self.__urls_to_crawl = []
        # Distinct URLs (md5) the crawler has crawled.
        self.__urls_crawled = Set()

    def start_crawl(self):
        # Push all start URLs to crawl.
        for start_url in self.__start_urls:
            if self.__url_is_allowed(start_url):
                url_md5 = md5.new(start_url).digest()
                if url_md5 not in self.__urls_crawled:
                    self.__urls_crawled.add(url_md5)
                    self.__urls_to_crawl.append(start_url)

        while self.__urls_to_crawl:
            try:
                # Pop out the first URL.
                url_to_crawl = self.__urls_to_crawl.pop(0)
                response = request.get(url_to_crawl, params=self.__query_params, retry_interval=self.__sleep_time)
                response_text = response.read().decode('utf-8', 'ignore')
                log.info('Crawled <%s>' % url_to_crawl)
                if self.__sleep_time > 0:
                    time.sleep(self.__sleep_time)

                html_element = fromstring(response_text)
                # Makes all links in the document absolute.
                html_element.make_links_absolute(url_to_crawl)
                # Extract all links in the document.
                link_elements = html_element.xpath('//a[@href]')
                for link_element in link_elements:
                    url = link_element.attrib['href']
                    # Add the URL if its domain is allowed, and has not been crawled.
                    url_md5 = md5.new(url).digest()
                    if  self.__url_is_allowed(url) and url_md5 not in self.__urls_crawled:
                        self.__urls_crawled.add(url_md5)
                        self.__urls_to_crawl.append(url)

                # Customized stuff provided by derived class.
                self.parse(html_element)

            except HTTPError, e:
                log.error('Server cannot fulfill the request <%s HTTP Error %s: %s>' % (url_to_crawl, e.code, e.msg))
            except URLError, e:
                log.error('Failed to reach server <%s Reason: %s>' % (url_to_crawl, e.reason))
            except Exception, e:
                log.error('Unknow exception: %s <%s>' % (e, url_to_crawl))

    def __url_is_allowed(self, url):
        # Return True if the domain of url is in allowed list, otherwise False.
        hostname = urlparse(url).hostname
        if hostname:
            for domain in self.__allowed_domains:
                if hostname.endswith(domain):
                    return True
        return False

    def parse(self, response):
        pass

if __name__ == '__main__':
    wc = WebCrawler(start_urls=['http://movie.douban.com/tag/'], allowed_domains=['movie.douban.com'],
                    query_params={'apikey': '05bc4743e8f8808a1134d5cbbae9819e'}, sleep_time=1.5)
    wc.start_crawl()
