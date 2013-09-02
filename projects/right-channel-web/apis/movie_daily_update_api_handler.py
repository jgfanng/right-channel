'''
Created on Mar 13, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from handlers.base_handler import BaseHandler, user_profile
from settings import mongodb, settings
from utilities import JSONEncoderExt
import datetime
import json
import tornado.gen
import tornado.web

class MovieDailyUpdateHandler(BaseHandler):
    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, movie_id):
        """Get latest movies which can be played or downloaded.

        :query string start: Start index of the movie list (optional, $start >= 0).
        :query string limit: Limited number of movies in a single request (optional, $movies_per_page >= $limit > 0).

        This API doesn't need to be authorized.
        """
#         user = self.params.get('user')
#         if not user:
#             raise tornado.web.HTTPError(401)  # Unauthorized
#
#         user_id = user.get('_id')
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

        # get latest movies
        try:
            # TODO: filter watched
            result, error = yield tornado.gen.Task(mongodb['movies'].find,
                                                   {},
                                                   fields={'summary': 0},
                                                   skip=start,
                                                   limit=limit,
                                                   sort=[('available_at', -1)])
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
