'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler

class HomeHandler(BaseHandler):
    def initialize(self):
        super(HomeHandler, self).initialize()
        self.params['site_nav'] = '/'

    def get(self):
        self.render('index.html')
