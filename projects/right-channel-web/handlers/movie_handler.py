'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler

class MovieHandler(BaseHandler):
    def get(self):
        self.render('movie/new.html')
