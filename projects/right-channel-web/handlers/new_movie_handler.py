'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, VIEW_FORMATS, IMAGE_TEXT_FORMAT
from utils.settings import collections, settings
import datetime
import tornado.web

class NewMovieHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.__view_format = self.get_argument('view-format', None)
        if self.__view_format not in VIEW_FORMATS:
            self.__view_format = IMAGE_TEXT_FORMAT

        collections['movies'].find(
            {'_release_date': {'$lte': datetime.datetime.utcnow()}},
            fields=settings['movie']['response']['verbose'],
            limit=50,
            sort=[('_release_date', -1)],
            callback=self._on_response)

    def _on_response(self, response, error):
        if error:
            raise tornado.web.HTTPError(500)

        self.render('movie/new_page.html', movies=response, view_format=self.__view_format)
