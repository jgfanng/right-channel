'''
Created on Jan 11, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler
from utils.json_encoder_ext import JSONEncoderExt
from utils.settings import settings, collections
import datetime
import json
import tornado.web

class MoviesHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        year = self.get_argument('year', None)
        type = self.get_argument('type', None)
        country = self.get_argument('country', None)
        min_douban_rating = self.get_argument('min-douban-rating', None)
        max_douban_rating = self.get_argument('max-douban-rating', None)
        start_date = self.get_argument('start-date', None)
        end_date = self.get_argument('end-date', None)
        filter = self.get_argument('filter', None)
        self.__start = self.get_argument('start', None)
        self.__count = self.get_argument('count', None)
        sort_by = self.get_argument('sort-by', None)

        query = {}
        if year:
            query['year'] = year
        if type:
            query['type'] = type
        if country:
            query['country'] = country
        if min_douban_rating and max_douban_rating:
            try:
                min_douban_rating = float(min_douban_rating)
                max_douban_rating = float(max_douban_rating)
                query['douban_rating'] = {'$gte': min_douban_rating, '$lte': max_douban_rating}
            except:
                pass
        elif min_douban_rating:
            try:
                min_douban_rating = float(min_douban_rating)
                query['douban_rating'] = {'$gte': min_douban_rating}
            except:
                pass
        elif max_douban_rating:
            try:
                max_douban_rating = float(max_douban_rating)
                query['douban_rating'] = {'$lte': max_douban_rating}
            except:
                pass
        if start_date and end_date:
            try:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                query['min_pubdate'] = {'$gte': start_date, '$lte': end_date}
            except:
                pass
        elif start_date:
            try:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                query['min_pubdate'] = {'$gte': start_date}
            except:
                pass
        elif end_date:
            try:
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                query['min_pubdate'] = {'$lte': end_date}
            except:
                pass
        if filter == 'online':
            query['source'] = {'$exists': 1}
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
                if self.__count <= 0 or self.__count > settings['movie']['response']['max_count']:
                    self.__count = settings['movie']['response']['max_count']
            except:
                self.__count = settings['movie']['response']['max_count']
        else:
            self.__count = settings['movie']['response']['max_count']
        if sort_by == 'publish-date':
            sort_by = [('min_pubdate', -1)]
        elif sort_by == 'douban-rating':
            sort_by = [('douban_rating', -1)]
        else:
            sort_by = None

        collections['movies'].find(
            query,
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
