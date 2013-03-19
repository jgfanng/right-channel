'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, user_profile
import tornado.gen
import tornado.web

class HomeHandler(BaseHandler):
    def initialize(self):
        self.params['site_nav'] = '/'

    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.render('index.html')
