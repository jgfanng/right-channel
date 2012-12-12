# -*- coding: utf-8 -*-

'''
Created on Dec 13, 2012

@author: Fang Jiaguo
'''
from crawlers.douban_crawler import DoubanCrawler

dc = DoubanCrawler(start_urls=[
                               'http://movie.douban.com/tag/',  # 豆瓣电影标签
                               'http://movie.douban.com/top250?format=text',  # 豆瓣电影250
                               'http://movie.douban.com/chart',  # 排行榜
                               'http://movie.douban.com/nowplaying/',  # 正在上映
                               'http://movie.douban.com/coming'  # 即将上映
                               ],
                   allowed_url_res=[
                                    '^http://movie\.douban\.com/tag/[^?]*(\?start=[0-9]+&type=T)?$',  # 豆瓣电影标签
                                    '^http://movie\.douban\.com/subject/[0-9]+/?$'  # 电影主页
                                    ],
                   additional_qs={'APIKEY': '05bc4743e8f8808a1134d5cbbae9819e'},
                   sleep_time=1.3)
dc.start_crawl()
