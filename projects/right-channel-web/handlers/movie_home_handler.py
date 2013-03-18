# -*- coding: utf-8 -*-
'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, authenticated_async
from settings import settings
from utilities import first_element
import tornado

class MovieHomeHandler(BaseHandler):
    def initialize(self):
        super(MovieHomeHandler, self).initialize()
        self.params['site_nav'] = 'movie'
        self.params['genre'] = first_element(settings['movie']['filters']['genres'])
        self.params['country'] = first_element(settings['movie']['filters']['countries'])
        self.params['year'] = first_element(settings['movie']['filters']['years'])
        self.params['sort'] = first_element(settings['movie']['presentation']['sort'])
        self.params['resource'] = first_element(settings['movie']['presentation']['resource'])

    @authenticated_async
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.params['genre'] = self.get_argument('genre', first_element(settings['movie']['filters']['genres']))
        if self.params['genre'] not in settings['movie']['filters']['genres']:
            self.params['genre'] = first_element(settings['movie']['filters']['genres'])

        self.params['country'] = self.get_argument('country', first_element(settings['movie']['filters']['countries']))
        if self.params['country'] not in settings['movie']['filters']['countries']:
            self.params['country'] = first_element(settings['movie']['filters']['countries'])

        self.params['year'] = self.get_argument('year', first_element(settings['movie']['filters']['years']))
        if self.params['year'] not in settings['movie']['filters']['years']:
            self.params['year'] = first_element(settings['movie']['filters']['years'])

        self.params['sort'] = self.get_argument('sort', first_element(settings['movie']['presentation']['sort']))
        if self.params['sort'] not in settings['movie']['presentation']['sort']:
            self.params['sort'] = first_element(settings['movie']['presentation']['sort'])

        self.params['resource'] = self.get_argument('resource', first_element(settings['movie']['presentation']['resource']))
        if self.params['resource'] not in settings['movie']['presentation']['resource']:
            self.params['resource'] = first_element(settings['movie']['presentation']['resource'])

        self.render('movie/movie_home_page.html')
