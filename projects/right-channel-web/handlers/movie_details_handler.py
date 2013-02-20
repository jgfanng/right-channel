'''
Created on Jan 21, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from handlers.base_handler import BaseHandler, authenticated_async
from settings import collections, settings
import tornado.web

class MovieDetailsHandler(BaseHandler):
    def initialize(self):
        super(MovieDetailsHandler, self).initialize()
        self.params['site_nav'] = 'movie'

    @authenticated_async()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, movie_id):
        try:
            response, error = yield tornado.gen.Task(collections['movies'].find_one,
                                                     {'_id': ObjectId(movie_id)},
                                                     fields=settings['movie']['response']['verbose'])
        except:
            raise tornado.web.HTTPError(500)

        if error.get('error'):
            raise tornado.web.HTTPError(500)

        self.params['movie'] = response[0]
        self.render('movie/movie_details_page.html')
