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

class MovieRecommendationHandler(BaseHandler):
    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        """Get recommendations for current user.
        
        Accepted query strings: start(optional), limit(optional).
        """
        user = self.params.get('user')
        if not user:
            raise tornado.web.HTTPError(401)  # Unauthorized

        user_id = user.get('_id')
        try:
            start = self.get_argument('start', 0)
            start = int(start)
        except:
            start = 0
        if start < 0:
            start = 0
        try:
            limit = self.get_argument('limit', settings['movie']['page_size'])
            limit = int(limit)
        except:
            limit = settings['application']['page_size']
        if limit <= 0 or limit > settings['movie']['page_size']:
            limit = settings['application']['page_size']

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

        movies = result[0]
        response = {
            'data': movies,
            'more': False if len(movies) < limit else True
        }

        self.write(json.dumps(response, cls=JSONEncoderExt))
        self.finish()
