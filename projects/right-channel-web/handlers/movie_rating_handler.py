# -*- coding: utf-8 -*-
'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, user_profile
import tornado

class MovieRatingHandler(BaseHandler):
    def initialize(self):
        self.params['site_nav'] = 'rating'

    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.render('movie/movie_rating_page.html')
