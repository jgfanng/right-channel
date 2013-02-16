'''
Created on Jan 21, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from handlers.base_handler import BaseHandler
from settings import collections, settings
import tornado.web

class MovieDetailsHandler(BaseHandler):
    def initialize(self):
        super(MovieDetailsHandler, self).initialize()
        self.params['site_nav'] = 'movie'

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, movie_id):
        email = self.get_secure_cookie('email')
        if email:
            try:
                response, error = yield tornado.gen.Task(collections['accounts'].find_one,
                                                         {'email': email},
                                                         fields={'email': 1, 'nick_name': 1})
            except:
                raise tornado.web.HTTPError(500)

            if 'error' in error and error['error']:
                raise tornado.web.HTTPError(500)

            user = response[0]
            if user:
                self.params['user'] = user
            else:
                self.clear_cookie('email')

        try:
            response, error = yield tornado.gen.Task(collections['movies'].find_one,
                                                     {'_id': ObjectId(movie_id)},
                                                     fields=settings['movie']['response']['verbose'])
        except:
            raise tornado.web.HTTPError(500)

        if 'error' in error and error['error']:
            raise tornado.web.HTTPError(500)

        self.params['movie'] = response[0]
        self.render('movie/movie_details_page.html')
