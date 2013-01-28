'''
Created on Jan 21, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from handlers.base_handler import BaseHandler
from utils.settings import collections, settings
import tornado.web

class MovieDetailsHandler(BaseHandler):
    def initialize(self):
        self.context = {'site_nav': 'movie'}

    @tornado.web.asynchronous
    def get(self, movie_id):
        collections['movies'].find_one(
            {'_id': ObjectId(movie_id)},
            fields=settings['movie']['response']['verbose'],
            callback=self._on_response)

    def _on_response(self, response, error):
        if error:
            raise tornado.web.HTTPError(500)
        if not response:
            # TODO: redirect
            raise tornado.web.HTTPError(404)

        self.render('movie/movie_details_page.html', movie=response, context=self.context)
