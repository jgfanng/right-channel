# -*- coding: utf-8 -*-
'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, authenticated_async
from settings import settings
import tornado

class MovieHomeHandler(BaseHandler):
    def initialize(self):
        super(MovieHomeHandler, self).initialize()
        self.params['site_nav'] = 'movie'
        self.params['genre'] = '全部'
        self.params['country'] = '全部'
        self.params['year'] = '全部'
        self.params['sort'] = '图文'
        self.params['view'] = '热度'

    @authenticated_async()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.params['genre'] = self.get_argument('genre', '全部')
        if self.params['genre'] not in settings['movie']['filters']['genres']:
            self.params['genre'] = '全部'
        self.params['country'] = self.get_argument('country', '全部')
        if self.params['country'] not in settings['movie']['filters']['countries']:
            self.params['country'] = '全部'
        self.params['year'] = self.get_argument('year', '全部')
        if self.params['year'] not in settings['movie']['filters']['years']:
            self.params['year'] = '全部'
        self.params['sort'] = self.get_argument('sort', None)
        if self.params['sort'] not in settings['movie']['presentation']['sort']:
            self.params['sort'] = '热度'
        self.params['view'] = self.get_argument('view', None)
        if self.params['view'] not in settings['movie']['presentation']['view']:
            self.params['view'] = '图文'

        self.render('movie/movie_home_page.html')
