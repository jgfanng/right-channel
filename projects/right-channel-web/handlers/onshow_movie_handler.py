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
        self.context = {'site_nav': 'movie', 'movie_nav': 'onshow', 'view_format': IMAGE_TEXT_FORMAT}

    @tornado.web.asynchronous
    def get(self):
        self.context['view_format'] = self.get_argument('view-format', None)
        if self.context['view_format'] not in VIEW_FORMATS:
            self.context['view_format'] = IMAGE_TEXT_FORMAT

        collections['movies'].find(
            {'_release_date': {'$lte': datetime.datetime.utcnow()}},
            fields=settings['movie']['response']['verbose'],
            limit=50,
            sort=[('_release_date', -1)],
            callback=self._on_response)

    def _on_response(self, response, error):
        if error:
            raise tornado.web.HTTPError(500)

        self.render('movie/onshow_page.html', movies=response, context=self.context)
