'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler

class HotMovieHandler(BaseHandler):
    def get(self):
        self.render('movie/hot_page.html')
