# -*- coding: utf-8 -*-

'''
Created on Dec 13, 2012

@author: Fang Jiaguo
'''
from crawlers.douban_crawler import DoubanCrawler, MOVIE_URL_RE, TAG_URL_RE

dc = DoubanCrawler(start_urls=[
                               'http://movie.douban.com/tag/',  # 豆瓣电影标签
                               'http://movie.douban.com/top250?format=text',  # 豆瓣电影250
                               'http://movie.douban.com/chart',  # 排行榜
                               'http://movie.douban.com/nowplaying/',  # 正在上映
                               'http://movie.douban.com/coming'  # 即将上映
                               ],
                   apikey='05bc4743e8f8808a1134d5cbbae9819e',
                   allowed_url_res=[
                                    MOVIE_URL_RE,  # 电影主页
                                    TAG_URL_RE  # 豆瓣电影标签
                                    ],
                   sleep_time=2)
dc.start_crawl()
