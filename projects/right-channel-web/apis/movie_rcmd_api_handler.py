# -*- coding: utf-8 -*-
'''
Created on Mar 11, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, user_profile
from settings import settings, mongodb
from utilities import JSONEncoderExt
import json
import tornado.gen
import tornado.web

class MovieRcmdAPIHandler(BaseHandler):
    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        """Get recommendations for current user.

        :query string start: Start index of the recommendation list (optional, $start >= 0).
        :query string limit: Limited number of recommendations in a single request (optional, $movies_per_page >= $limit > 0).

        This API need to be authorized.
        """
        user = self.params.get('user')
        if not user:
            raise tornado.web.HTTPError(401)  # Unauthorized

        user_id = user.get('_id')
        # ensure start
        start = self.get_argument('start', 0)
        try:
            start = int(start)
        except:
            start = 0
        if start < 0:
            start = 0
        # ensure limit
        limit = self.get_argument('limit', settings['movie']['movies_per_page'])
        try:
            limit = int(limit)
        except:
            limit = settings['movie']['movies_per_page']
        if limit <= 0 or limit > settings['movie']['movies_per_page']:
            limit = settings['movie']['movies_per_page']

        # get movie ids
        try:
            result, error = yield tornado.gen.Task(mongodb['movie.recommendations'].find,
                                                   {'user_id': user_id},
                                                   skip=start,
                                                   limit=limit,
                                                   sort=[('rating', -1)])
        except:
            raise tornado.web.HTTPError(500)

        if error.get('error'):
            raise tornado.web.HTTPError(500)

        # get real movie info
        movies = result[0]
        try:
            # TODO: order by predicted rating
            # TODO: filtering
            result, error = yield tornado.gen.Task(mongodb['movies'].find,
                                                   {'_id': {'$in': [movie.get('movie_id') for movie in movies]}})
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
