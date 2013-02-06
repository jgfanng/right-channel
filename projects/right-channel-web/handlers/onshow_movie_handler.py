# -*- coding: utf-8 -*-
'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, VIEW_FORMATS, IMAGE_TEXT_FORMAT
from settings import collections, settings
import datetime
import tornado.web

class OnshowMovieHandler(BaseHandler):
    def initialize(self):
        super(OnshowMovieHandler, self).initialize()
        self.context['site_nav'] = 'movie'
        self.context['movie_nav'] = 'onshow'
        self.context['view_format'] = IMAGE_TEXT_FORMAT

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        email = self.get_secure_cookie('email')
        if email:
            response, error = yield tornado.gen.Task(collections['accounts'].find_one, {'email': email})

            if 'error' in error and error['error']:
                self.render('movie/onshow_page.html', movies=[], op_result={'type': 'error', 'message': '尊敬的用户，当前操作无法完成，请联系管理员'})
                return

            self.user = response[0]

        self.context['view_format'] = self.get_argument('view-format', None)
        if self.context['view_format'] not in VIEW_FORMATS:
            self.context['view_format'] = IMAGE_TEXT_FORMAT

        response, error = yield tornado.gen.Task(collections['movies'].find,
                                                 {'_release_date': {'$lte': datetime.datetime.utcnow()}},
                                                 fields=settings['movie']['response']['verbose'],
                                                 limit=50,
                                                 sort=[('_release_date', -1)])

        if 'error' in error and error['error']:
            self.render('movie/onshow_page.html', movies=[], op_result={'type': 'error', 'message': '尊敬的用户，当前操作无法完成，请联系管理员'})
            return

        self.render('movie/onshow_page.html', movies=response[0])
