'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler
from utils.settings import collections, settings
import datetime
import tornado.web

class NewMovieHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        collections['movies'].find(
            {'_release_date': {'$lte': datetime.datetime.utcnow()}},
            fields=settings['movie']['response']['verbose'],
            limit=50,
            sort=[('_release_date', -1)],
            callback=self._on_response)

    def _on_response(self, response, error):
        if error:
            raise tornado.web.HTTPError(500)

        self.render('movie/new.html', movies=response)
