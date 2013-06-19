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
        :query string limit: Limited number of recommendations in a single request (optional, $upper_bound >= $limit > 0).

        This API need to be authorized.
        """
        user = self.params.get('user')
        if not user:
            raise tornado.web.HTTPError(401)  # Unauthorized

        user_id = user.get('_id')
        start = self.get_argument('start', 0)
        try:
            start = int(start)
        except:
            start = 0
        if start < 0:
            start = 0
        limit = self.get_argument('limit', settings['movie']['page_size'])
        try:
            limit = int(limit)
        except:
            limit = settings['application']['page_size']
        if limit <= 0 or limit > settings['movie']['page_size']:
            limit = settings['application']['page_size']

        # get movie ids from "recommendations" collection
        try:
            result, error = yield tornado.gen.Task(mongodb['recommendations'].find,
                                                   {'user_id': user_id},
                                                   skip=start,
                                                   limit=limit,
                                                   sort=[('rating', -1)])
        except:
            raise tornado.web.HTTPError(500)

        if error.get('error'):
            raise tornado.web.HTTPError(500)

        # get real movie info from "movies" collection
        movies = result[0]
        try:
            # TODO: order by predicted rating
            result, error = yield tornado.gen.Task(mongodb['movies'].find,
                                                   {'_id': {'$in': [movie.get('movie_id') for movie in movies]}})
        except:
            raise tornado.web.HTTPError(500)

        if error.get('error'):
            raise tornado.web.HTTPError(500)

        movies = result[0]
        response = {
            'movies': movies,
            'more': False if len(movies) < limit else True
        }

        self.write(json.dumps(response, cls=JSONEncoderExt))
        self.finish()
