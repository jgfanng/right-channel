# -*- coding: utf-8 -*-
'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, authenticated_async
from settings import settings, mongodb
from util import first_element, last_element, get_body
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
        self.params['view'] = first_element(settings['movie']['presentation']['view'])

    @authenticated_async()
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

        self.params['view'] = self.get_argument('view', first_element(settings['movie']['presentation']['view']))
        if self.params['view'] not in settings['movie']['presentation']['view']:
            self.params['view'] = first_element(settings['movie']['presentation']['view'])

        query = {}
        if self.params['genre'] == last_element(settings['movie']['filters']['genres']):
            query['genres'] = {'$nin': get_body(settings['movie']['filters']['genres'])}
        elif self.params['genre'] != first_element(settings['movie']['filters']['genres']):
            query['genres'] = self.params['genre']

        if self.params['country'] == last_element(settings['movie']['filters']['countries']):
            query['countries'] = {'$nin': get_body(settings['movie']['filters']['countries'])}
        elif self.params['country'] != first_element(settings['movie']['filters']['countries']):
            query['countries'] = self.params['country']

        if self.params['year'] == last_element(settings['movie']['filters']['years']):
            query['year'] = {'$lt': '1980'}
        elif self.params['year'] == '80年代':
            query['year'] = {'$gte': '1980', '$lt': '1990'}
        elif self.params['year'] == '90年代':
            query['year'] = {'$gte': '1990', '$lt': '2000'}
        elif self.params['year'] == '00年代':
            query['year'] = {'$gte': '2000', '$lt': '2009'}
        elif self.params['year'] != first_element(settings['movie']['filters']['years']):
            query['year'] = self.params['year']

        try:
            response, error = yield tornado.gen.Task(mongodb['movies'].find,
                                                     query,
                                                     fields=settings['movie']['response']['verbose'],
                                                     skip=0,
                                                     limit=30)
        except:
            raise tornado.web.HTTPError(500)

        if error.get('error'):
            raise tornado.web.HTTPError(500)

        self.params['movies'] = response[0]
        self.render('movie/movie_home_page.html')
