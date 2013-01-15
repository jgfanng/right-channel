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
        genre = self.get_argument('genre', None)
        country = self.get_argument('country', None)
        min_douban_rating = self.get_argument('min-douban-rating', None)
        max_douban_rating = self.get_argument('max-douban-rating', None)
        min_release_date = self.get_argument('min-release-date', None)
        max_release_date = self.get_argument('max-release-date', None)
        filter = self.get_argument('filter', None)
        start = self.get_argument('start', None)
        count = self.get_argument('count', None)
        sort_by = self.get_argument('sort-by', None)

        query = {}
        if year:
            query['year'] = year
        if genre:
            query['genre'] = genre
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
        if min_release_date and max_release_date:
            try:
                min_release_date = datetime.datetime.strptime(min_release_date, '%Y-%m-%d')
                max_release_date = datetime.datetime.strptime(max_release_date, '%Y-%m-%d')
                query['_release_date'] = {'$gte': min_release_date, '$lte': max_release_date}
            except:
                pass
        elif min_release_date:
            try:
                min_release_date = datetime.datetime.strptime(min_release_date, '%Y-%m-%d')
                query['_release_date'] = {'$gte': min_release_date}
            except:
                pass
        elif max_release_date:
            try:
                max_release_date = datetime.datetime.strptime(max_release_date, '%Y-%m-%d')
                query['_release_date'] = {'$lte': max_release_date}
            except:
                pass
        if filter == 'online':
            query['source'] = {'$exists': 1}
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
        if sort_by == 'release-date':
            sort_by = [('_release_date', -1)]
        elif sort_by == 'douban-rating':
            sort_by = [('douban_rating', -1)]
        else:
            sort_by = None

        collections['movies'].find(
            query,
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
