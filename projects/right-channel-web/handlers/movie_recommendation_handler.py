# -*- coding: utf-8 -*-
'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, user_profile
import tornado

class MovieRecommendationHandler(BaseHandler):
    def initialize(self):
        self.params['site_nav'] = 'recommendation'

    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        # TODO: need to login
        self.render('movie/movie_recommendation_page.html')
