'''
Created on Jan 13, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler
from utils.json_encoder_ext import JSONEncoderExt
from utils.settings import collections, settings
import json
import tornado.web

class HotHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, hot_type):
        if hot_type == 'week':
            sort_by = [('watch_times.last_week', -1)]
        elif hot_type == 'month':
            sort_by = [('watch_times.last_month', -1)]
        elif hot_type == 'history':
            sort_by = [('watch_times.history', -1)]

        self.__start = self.get_argument('start', None)
        self.__count = self.get_argument('count', None)
        if self.__start:
            try:
                self.__start = int(self.__start)
                if self.__start < 0:
                    self.__start = 0
            except:
                self.__start = 0
        else:
            self.__start = 0
        if self.__count:
            try:
                self.__count = int(self.__count)
                if self.__count <= 0 or self.__count > self.config['movie']['response']['max_count']:
                    self.__count = self.config['movie']['response']['max_count']
            except:
                self.__count = self.config['movie']['response']['max_count']
        else:
            self.__count = self.config['movie']['response']['max_count']

        collections['movies'].find(
            fields=settings['movie']['response']['verbose'],
            skip=self.__start,
            limit=self.__count,
            sort=sort_by,
            callback=self._on_response)

    def _on_response(self, response, error):
        if error:
            raise tornado.web.HTTPError(500)

        result = {'start': self.__start, 'count': self.__count, 'movies': []}
        for movie in response:
            movie['id'] = movie.pop('_id')
            result['movies'].append(movie)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result, cls=JSONEncoderExt))
        self.finish()
