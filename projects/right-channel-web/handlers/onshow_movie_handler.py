# -*- coding: utf-8 -*-
'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, VIEW_FORMATS, IMAGE_TEXT_FORMAT, \
    authenticated_async
from settings import collections, settings
import datetime
import tornado

class OnshowMovieHandler(BaseHandler):
    def initialize(self):
        super(OnshowMovieHandler, self).initialize()
        self.params['site_nav'] = 'movie'
        self.params['movie_nav'] = 'onshow'
        self.params['view_format'] = IMAGE_TEXT_FORMAT

    @authenticated_async()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.params['view_format'] = self.get_argument('view-format', None)
        if self.params['view_format'] not in VIEW_FORMATS:
            self.params['view_format'] = IMAGE_TEXT_FORMAT

        try:
            response, error = yield tornado.gen.Task(collections['movies'].find,
                                                     {'_release_date': {'$lte': datetime.datetime.utcnow()}},
                                                     fields=settings['movie']['response']['verbose'],
                                                     limit=50,
                                                     sort=[('_release_date', -1)])
        except:
            raise tornado.web.HTTPError(500)

        if error.get('error'):
            raise tornado.web.HTTPError(500)

        self.params['movies'] = response[0]
        self.render('movie/onshow_page.html')
