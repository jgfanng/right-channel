# -*- coding: utf-8 -*-
'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, authenticated_async
import tornado

class MovieHomeHandler(BaseHandler):
    def initialize(self):
        super(MovieHomeHandler, self).initialize()
        self.params['site_nav'] = 'movie'

    @authenticated_async()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.render('movie/movie_home_page.html')
