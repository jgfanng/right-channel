'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, get_current_user_info
import tornado.gen
import tornado.web

class HomeHandler(BaseHandler):
    def initialize(self):
        super(HomeHandler, self).initialize()
        self.params['site_nav'] = '/'

    @get_current_user_info()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.render('index.html')
