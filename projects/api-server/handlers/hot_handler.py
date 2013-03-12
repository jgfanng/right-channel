'''
Created on Jan 13, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler
from utilities.json_encoder_ext import JSONEncoderExt
from utilities.settings import collections, settings
import json
import tornado.web

class HotHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, period):
        if period == 'week':
            sort_by = [('view.last_week', -1)]
        elif period == 'month':
            sort_by = [('view.last_month', -1)]
        elif period == 'history':
            sort_by = [('view.history', -1)]

        start = self.get_argument('start', None)
        count = self.get_argument('count', None)
        if start:
            try:
                start = int(start)
                if start < 0:
                    start = 0
            except:
                start = 0
        else:
            start = 0
        if count:
            try:
                count = int(count)
                if count <= 0 or count > settings['movie']['response']['max_count']:
                    count = settings['movie']['response']['max_count']
            except:
                count = settings['movie']['response']['max_count']
        else:
            count = settings['movie']['response']['max_count']

        collections['movies'].find(
            fields=settings['movie']['response']['verbose'],
            skip=start,
            limit=count,
            sort=sort_by,
            callback=self._on_response)

    def _on_response(self, response, error):
        if error:
            raise tornado.web.HTTPError(500)

        result = {'movies': []}
        for movie in response:
            movie['id'] = movie.pop('_id')
            result['movies'].append(movie)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result, cls=JSONEncoderExt))
        self.finish()
