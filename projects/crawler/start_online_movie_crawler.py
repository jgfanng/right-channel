'''
Created on Apr 12, 2013

@author: Fang Jiaguo
'''
from crawlers.online_movie_crawler import IQIYIMovieCrawler, OnlineMovieMatcher

if __name__ == '__main__':
    threads = [
        IQIYIMovieCrawler(),
        OnlineMovieMatcher()
    ]
    for thread in threads:
        thread.start()
