# -*- coding: utf-8 -*-
'''
Created on Mar 11, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, user_profile
from settings import mongodb
from utilities import JSONEncoderExt
import json
import tornado.gen
import tornado.web

class MovieCategoryAPIHandler(BaseHandler):
    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        """Movie category API.

        :query string sort: Sort result by which field (optional).
        :query string start: Start index of the movie list (optional, TOTAL_ACCESSABLE_MOVIES > $start >= 0).
        :query string limit: Limited number of movies in a single request (optional, MOVIES_PER_REQUEST >= $limit > 0).

        This API doesn't need to be authorized.
        """
        # query string: sort
        sort_field = self.get_argument('sort', None)
        if sort_field not in self.SORT_FIELDS:
            sort_field = None
        if sort_field:
            sort = [(sort_field, -1)]
        else:
            sort = None

        # query string: start
        start = self.get_argument('start', 0)
        try:
            start = int(start)
        except:
            start = 0
        if start < 0:
            start = 0

        # query string: limit
        limit = self.get_argument('limit', self.MOVIES_PER_REQUEST)
        try:
            limit = int(limit)
        except:
            limit = self.MOVIES_PER_REQUEST
        if limit <= 0 or limit > self.MOVIES_PER_REQUEST:
            limit = self.MOVIES_PER_REQUEST

        try:
            result, error = yield tornado.gen.Task(mongodb['movies'].find, fields={'summary': 0}, skip=start, limit=limit, sort=sort)
        except:
            raise tornado.web.HTTPError(500)
        if error.get('error'):
            raise tornado.web.HTTPError(500)

        movies = result[0]
        response = {
            'movies': movies,
            'total': len(movies),
            'start': start,
            'limit': limit
        }
        self.write(json.dumps(response, cls=JSONEncoderExt))
        self.finish()
