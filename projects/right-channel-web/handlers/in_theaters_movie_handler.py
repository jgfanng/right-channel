# -*- coding: utf-8 -*-
'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, VIEW_FORMATS, IMAGE_TEXT_FORMAT, \
    authenticated_async
from settings import settings, mongodb
import tornado

class InTheatersMovieHandler(BaseHandler):
    def initialize(self):
        super(InTheatersMovieHandler, self).initialize()
        self.params['site_nav'] = 'movie'
        self.params['movie_nav'] = 'intheaters'
        self.params['view_format'] = IMAGE_TEXT_FORMAT

    @authenticated_async()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.params['view_format'] = self.get_argument('view-format', None)
        if self.params['view_format'] not in VIEW_FORMATS:
            self.params['view_format'] = IMAGE_TEXT_FORMAT

        try:
            response, error = yield tornado.gen.Task(mongodb['movies.collections'].find_one,
                                                     {'id': 'in_theaters'})
        except:
            raise tornado.web.HTTPError(500)

        if error.get('error'):
            raise tornado.web.HTTPError(500)

        if response[0]:
            try:
                response, error = yield tornado.gen.Task(mongodb['movies'].find,
                                                         {'douban.id': {'$in': response[0].get('douban_ids')}},
                                                         fields=settings['movie']['response']['verbose'])
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

            self.params['movies'] = response[0]
        else:
            self.params['movies'] = []

        self.render('movie/in_theaters_page.html')
