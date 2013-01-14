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
        min_pubdate = self.get_argument('min-pubdate', None)
        max_pubdate = self.get_argument('max-pubdate', None)
        filter = self.get_argument('filter', None)
        start = self.get_argument('start', None)
        count = self.get_argument('count', None)
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
        if min_pubdate and max_pubdate:
            try:
                min_pubdate = datetime.datetime.strptime(min_pubdate, '%Y-%m-%d')
                max_pubdate = datetime.datetime.strptime(max_pubdate, '%Y-%m-%d')
                query['_pubdate'] = {'$gte': min_pubdate, '$lte': max_pubdate}
            except:
                pass
        elif min_pubdate:
            try:
                min_pubdate = datetime.datetime.strptime(min_pubdate, '%Y-%m-%d')
                query['_pubdate'] = {'$gte': min_pubdate}
            except:
                pass
        elif max_pubdate:
            try:
                max_pubdate = datetime.datetime.strptime(max_pubdate, '%Y-%m-%d')
                query['_pubdate'] = {'$lte': max_pubdate}
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
        if sort_by == 'publish-date':
            sort_by = [('_pubdate', -1)]
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
