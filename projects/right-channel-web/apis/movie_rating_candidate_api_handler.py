# -*- coding: utf-8 -*-
'''
Created on Mar 11, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, user_profile
from settings import settings, mongodb
from utilities import JSONEncoderExt
import json
import random
import tornado.gen
import tornado.web

class MovieRatingCandidateAPIHandler(BaseHandler):

    MAX_CANIDIDATES = 100

    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        """Get rating candidates.

        :query string start: Start index of the rating candidates (optional, $start >= 0).
        :query string end: End index (exclusive) of the rating candidates (optional, MAX_CANIDIDATES+$start >= $end > $start).
        :query string pick: Number of candidates randomly picked within [$start, $end) (optional, $movies_per_page >= $pick > 0).

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
        # ensure end
        end = self.get_argument('end', 0)
        try:
            end = int(end)
        except:
            end = 0
        if end <= start or (end - start) > self.MAX_CANIDIDATES:
            end = start + self.MAX_CANIDIDATES
        # ensure pick
        pick = self.get_argument('pick', settings['movie']['movies_per_page'])
        try:
            pick = int(pick)
        except:
            pick = settings['movie']['movies_per_page']
        if pick <= 0 or pick > settings['movie']['movies_per_page']:
            pick = settings['movie']['movies_per_page']
        if pick > end - start:
            pick = end - start

        try:
            # TODO: if user is logged in
            result, error = yield tornado.gen.Task(mongodb['movies'].find,
                                                   {},
                                                   fields={'summary': 0},
                                                   skip=start,
                                                   limit=end - start,
                                                   sort=[('douban.collect_count', -1)])
        except:
            raise tornado.web.HTTPError(500)

        if error.get('error'):
            raise tornado.web.HTTPError(500)

        # randomly pick
        candidates = result[0]
        random_indices = sorted(random.sample(range(len(candidates)), min(pick, len(candidates))))
        movies = [candidates[index] for index in random_indices]
        response = {
            'movies': movies,
            'total': len(movies),
            'start': start,
            'end': end,
            'pick': pick
        }

        self.write(json.dumps(response, cls=JSONEncoderExt))
        self.finish()
