# -*- coding: utf-8 -*-

'''
Created on Nov 26, 2012

@author: Fang Jiaguo
'''
from crawlers.utilities import request
from crawlers.utilities.log import get_logger
from crawlers.utilities.mongodb import movies_store_collection
from crawlers.utilities.title_simplifier import simplify
from lxml.html import fromstring
from operator import itemgetter
from pymongo.errors import PyMongoError
from sets import Set
from urllib2 import HTTPError, URLError
from urlparse import urldefrag
import datetime
import md5
import re
import time

# douban api key
APIKEY = '05bc4743e8f8808a1134d5cbbae9819e'
# douban movie link regular expression
MOVIE_URL_RE = re.compile('^http://movie\.douban\.com/subject/[0-9]+/?$')
# detailed info descriptions
DETAILED_INFO_DESC = [u'导演:', u'编剧:', u'主演:', u'集数:', u'类型:', u'制片国家/地区:',
                      u'语言:', u'上映日期:', u'首播日期:', u'片长:', u'单集片长:', u'又名:',
                      u'IMDb链接:', u'官方网站:', u'季数:', u'官方小站:']

class DoubanCrawler():
    '''
    Crawler for douban move site (http://movie.douban.com/).
    '''

    logger = get_logger('DoubanCrawler', 'douban_crawler.log')

    def __init__(self, start_urls, allowed_url_res=None, query_strings=None, sleep_time=5):
        # A list of URLs where the crawler will begin to crawl from.
        self.start_urls = start_urls
        # An optional list of strings containing URL regex that this crawler is allowed to crawl.
        self.allowed_url_res = [re.compile(item) for item in allowed_url_res]
        # Query string parameters when sending a request.
        self.__query_strings = query_strings
        # Sleep for throttle.
        self.sleep_time = sleep_time
        # A list of URLs the crawler will crawl.
        self.__uncrawled_movie_urls = []
        self.__uncrawled_nonmovie_urls = []
        # Distinct URLs (md5) the crawler has crawled.
        self.__crawled_urls = Set()
        # Total movies crawled.
        self.__total_movies_crawled = 0

    def start_crawl(self):
        DoubanCrawler.logger.info('==========Start to crawl douban movies==========')
        self.__start_crawl()
        DoubanCrawler.logger.info('==========Finish crawling douban movies==========')
        DoubanCrawler.logger.info('==========Totally crawled %s movies==========' % len(self.__crawled_urls))

    def __start_crawl(self):
        # Push start URLs as seeds.
        for start_url in self.start_urls:
            url_md5 = md5.new(start_url.encode('utf-8')).digest()
            if url_md5 not in self.__crawled_urls:
                self.__crawled_urls.add(url_md5)
                if MOVIE_URL_RE.match(start_url):
                    self.__uncrawled_movie_urls.append(start_url)
                else:
                    self.__uncrawled_nonmovie_urls.append(start_url)

        while self.__uncrawled_movie_urls or self.__uncrawled_nonmovie_urls:
            try:
                # Pop out the first URL.
                if self.__uncrawled_movie_urls:
                    url_to_crawl = self.__uncrawled_movie_urls.pop(0)
                    is_movie_url = True
                else:
                    url_to_crawl = self.__uncrawled_nonmovie_urls.pop(0)
                    is_movie_url = False
                response = request.get(url_to_crawl.encode('utf-8'), additional_qs=self.__query_strings, retry_interval=self.sleep_time)
                response_text = response.read()
                DoubanCrawler.logger.debug('Crawled <%s>' % url_to_crawl)
                if self.sleep_time > 0:
                    time.sleep(self.sleep_time)

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
                            if MOVIE_URL_RE.match(url_in_page):
                                self.__uncrawled_movie_urls.append(url_in_page)
                            else:
                                self.__uncrawled_nonmovie_urls.append(url_in_page)

                if is_movie_url:
                    movie_info = self.__get_movie_info(url_to_crawl, html_element)
                    missed_fields = []
                    fields = ['year', 'titles', 'directors', 'writers', 'casts', 'types', 'countries',
                              'languages', 'pubdates', 'durations', 'image', 'summary']
                    for field in fields:
                        if field not in movie_info:
                            missed_fields.append(field)
                    if 'score' not in movie_info['douban']:
                        missed_fields.append('score')
                    if missed_fields:
                        DoubanCrawler.logger.warning('%s not found on page <%s>. Please check whether the xpath has changed' % (', '.join(missed_fields), url_to_crawl))

                    #----------Save to Mongodb-------------------------------
                    try:
                        if 'simp_titles' in movie_info:
                            simp_titles = movie_info.pop('simp_titles')
                            movies_store_collection.update({'id': movie_info['id']}, {'$set': movie_info, '$addToSet': {'simp_titles': {'$each': simp_titles}}}, upsert=True)
                        else:
                            movies_store_collection.update({'id': movie_info['id']}, {'$set': movie_info}, upsert=True)
                    except PyMongoError, e:
                        DoubanCrawler.logger.error('%s <%s %s>' %
                                                   (e, movie_info['year'] if 'year' in movie_info else None, movie_info['titles'][0] if 'titles' in movie_info else None))
                        continue
                    #--------------------------------------------------------

                    self.__total_movies_crawled += 1
                    DoubanCrawler.logger.info('Crawled movie #%s <%s %s> C(%s) UM(%s) UT(%s)' %
                                              (self.__total_movies_crawled, movie_info['year'] if 'year' in movie_info else None, movie_info['titles'][0] if 'titles' in movie_info else None, len(self.__crawled_urls), len(self.__uncrawled_movie_urls), len(self.__uncrawled_nonmovie_urls)))

            except HTTPError, e:
                DoubanCrawler.logger.error('Server cannot fulfill the request <%s %s %s>' % (url_to_crawl, e.code, e.msg))
            except URLError, e:
                DoubanCrawler.logger.error('Failed to reach server <%s %s>' % (url_to_crawl, e.reason))
            except Exception, e:
                DoubanCrawler.logger.error('%s <%s>' % (e, url_to_crawl))

    def __get_movie_info(self, url, html_element):
        '''
        Construct movie info from movie page.
        '''

        movie_info = {}

        # movie id
        if url.endswith('/'):
            movie_info['id'] = url[len('http://movie.douban.com/subject/'):-1]
        else:
            movie_info['id'] = url[len('http://movie.douban.com/subject/'):]

        # movie year
        movie_year_elements = html_element.xpath('/html/body/div/h1/span[@class="year"]')
        if movie_year_elements and movie_year_elements[0].text and movie_year_elements[0].text.strip():
            movie_info['year'] = movie_year_elements[0].text.strip()[1:-1]

        # movie titles
        movie_info['titles'] = []
        page_title_elements = html_element.xpath('/html/head/title')
        if page_title_elements and page_title_elements[0].text and page_title_elements[0].text.strip():
            if page_title_elements[0].text.strip().endswith(u'(豆瓣)'):
                page_title = page_title_elements[0].text.strip()[:-len(u'(豆瓣)')].strip()
                movie_info['titles'].append(page_title)

        movie_title_elements = html_element.xpath('/html/body/div/h1/span[@property="v:itemreviewed"]')
        if movie_title_elements and movie_title_elements[0].text and movie_title_elements[0].text.strip():
            # if page title exists
            if len(movie_info['titles']) > 0:
                movie_info['titles'] += [item.strip() for item in movie_title_elements[0].text.strip().split(movie_info['titles'][0]) if item.strip()]
            else:
                movie_info['titles'].append(movie_title_elements[0].text.strip())

        # movie image
        image_elements = html_element.xpath('/html/body/div/div/div/div/div/div/div/div/a[@class="nbg"]/img[@src]')
        if image_elements:
            movie_info['image'] = image_elements[0].attrib['src']

        # movie score
        movie_info['douban'] = {'link': url, 'last_updated': datetime.datetime.utcnow()}
        score_elements = html_element.xpath('/html/body/div/div/div/div/div/div/div/div/p/strong[@class="ll rating_num"]')
        if score_elements and score_elements[0].text and score_elements[0].text.strip():
            movie_info['douban']['score'] = score_elements[0].text.strip()

        # movie summary
        summary_elements = html_element.xpath('/html/body/div/div/div/div/div/div//span[@property="v:summary"]')
        if summary_elements and summary_elements[0].text and summary_elements[0].text.strip():
            movie_info['summary'] = summary_elements[0].text.strip()

        # detailed info area
        detailed_info_elements = html_element.xpath('/html/body/div/div/div/div/div/div/div/div[@id="info"]')
        if detailed_info_elements and detailed_info_elements[0].text_content() and detailed_info_elements[0].text_content().strip():
            detailed_info = self.__extract_detailed_info(detailed_info_elements[0].text_content().strip())
            if 'directors' in detailed_info:
                movie_info['directors'] = detailed_info['directors']
            if 'writers' in detailed_info:
                movie_info['writers'] = detailed_info['writers']
            if 'casts' in detailed_info:
                movie_info['casts'] = detailed_info['casts']
            if 'episodes' in detailed_info:
                movie_info['episodes'] = detailed_info['episodes']
            if 'types' in detailed_info:
                movie_info['types'] = detailed_info['types']
            if 'countries' in detailed_info:
                movie_info['countries'] = detailed_info['countries']
            if 'languages' in detailed_info:
                movie_info['languages'] = detailed_info['languages']
            if 'pubdates' in detailed_info:
                movie_info['pubdates'] = detailed_info['pubdates']
            if 'durations' in detailed_info:
                movie_info['durations'] = detailed_info['durations']
            if 'alt_titles' in detailed_info:
                for alt_title in detailed_info['alt_titles']:
                    if alt_title not in movie_info['titles']:
                        movie_info['titles'].append(alt_title)
            if 'imdb_name' in detailed_info:
                movie_info['imdb'] = {'name': detailed_info['imdb_name'], 'last_updated': datetime.datetime.utcnow()}

        # simplify titles
        for title in movie_info['titles']:
            simp_title = simplify(title)
            if simp_title not in movie_info['titles']:
                if 'simp_titles' not in movie_info:
                    movie_info['simp_titles'] = []
                if simp_title not in movie_info['simp_titles']:
                    movie_info['simp_titles'].append(simp_title)

        return movie_info

    def __extract_detailed_info(self, info_text):
        '''
        Extract detailed info from the following info_text.
        导演: 弗兰克·德拉邦特
        编剧: 弗兰克·德拉邦特 / 罗伯特·柯克曼
        主演: 安德鲁·林肯 / 莎拉·韦恩·卡丽丝 / 大卫·莫瑞瑟 / 劳瑞·侯登 / 史蒂文·元 / 钱德勒·里格斯 / 斯科特·威尔森 / 劳伦·科汉 / 诺曼·瑞杜斯
        类型: 剧情 / 恐怖 / 灾难
        官方网站: http://www.amctv.com/shows/the-walking-dead
        制片国家/地区: 美国
        语言: 英语
        首播日期: 2012-10-14
        季数: 3
        集数: 16
        单集片长: 45分钟
        IMDb链接: tt2107527
        '''

        desc_pos = []
        for desc in DETAILED_INFO_DESC:
            desc_pos.append((desc, info_text.find(desc)))
        desc_pos.sort(key=itemgetter(1))

        # remove overlap, e.g. u'片长:' and u'单集片长:'
        while True:
            find_overlap = False
            for i in range(len(desc_pos)):
                if desc_pos[i][1] < 0:
                    continue
                if i + 1 < len(desc_pos) and desc_pos[i][1] + len(desc_pos[i][0]) > desc_pos[i + 1][1]:
                    desc_pos.pop(i + 1)
                    find_overlap = True
                    break
            if not find_overlap:
                break

        detailed_info = {}
        for i in range(len(desc_pos)):
            if desc_pos[i][1] < 0:
                continue
            value = info_text[desc_pos[i][1] + len(desc_pos[i][0]):desc_pos[i + 1][1] if i + 1 < len(desc_pos) else len(info_text)].strip()
            if value:
                if desc_pos[i][0] == u'导演:':
                    directors = [item.strip() for item in value.split(' / ') if item.strip()]
                    if directors:
                        detailed_info['directors'] = directors
                elif desc_pos[i][0] == u'编剧:':
                    writers = [item.strip() for item in value.split(' / ') if item.strip()]
                    if writers:
                        detailed_info['writers'] = writers
                elif desc_pos[i][0] == u'主演:':
                    casts = [item.strip() for item in value.split(' / ') if item.strip()]
                    if casts:
                        detailed_info['casts'] = casts
                elif desc_pos[i][0] == u'集数:':
                    detailed_info['episodes'] = value
                elif desc_pos[i][0] == u'类型:':
                    types = [item.strip() for item in value.split(' / ') if item.strip()]
                    if types:
                        detailed_info['types'] = types
                elif desc_pos[i][0] == u'制片国家/地区:':
                    countries = [item.strip() for item in value.split(' / ') if item.strip()]
                    if countries:
                        detailed_info['countries'] = countries
                elif desc_pos[i][0] == u'语言:':
                    languages = [item.strip() for item in value.split(' / ') if item.strip()]
                    if languages:
                        detailed_info['languages'] = languages
                elif desc_pos[i][0] == u'上映日期:' or desc_pos[i][0] == u'首播日期:':
                    pubdates = [item.strip() for item in value.split(' / ') if item.strip()]
                    if pubdates:
                        detailed_info['pubdates'] = pubdates
                elif desc_pos[i][0] == u'片长:' or desc_pos[i][0] == u'单集片长:':
                    durations = [item.strip() for item in value.split(' / ') if item.strip()]
                    if durations:
                        detailed_info['durations'] = durations
                elif desc_pos[i][0] == u'又名:':
                    alt_titles = [item.strip() for item in value.split(' / ') if item.strip()]
                    if alt_titles:
                        detailed_info['alt_titles'] = alt_titles
                elif desc_pos[i][0] == u'IMDb链接:':
                    detailed_info['imdb_name'] = value

        return detailed_info

    def __url_is_allowed(self, url):
        # Return True if URL pattern is allowed, otherwise False.
        if not self.allowed_url_res:
            return True

        for re in self.allowed_url_res:
            if re.match(url):
                return True

        return False
