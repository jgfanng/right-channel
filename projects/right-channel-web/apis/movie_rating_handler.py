'''
Created on Mar 13, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from handlers.base_handler import BaseHandler, user_profile
from settings import mongodb
import datetime
import tornado.gen
import tornado.web

class MovieRatingHandler(BaseHandler):
    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self, movie_id):
        user = self.params.get('user')
        if user:
            user_id = user.get('_id')
            rating = self.get_argument('rating')
            try:
                rating = float(rating)
            except:
                raise tornado.web.HTTPError(400)
            if rating < 0 or rating > 5:
                raise tornado.web.HTTPError(400)

            try:
                _, error = yield tornado.gen.Task(mongodb['ratings'].update,
                                                  {'user_id': user_id, 'movie_id': ObjectId(movie_id)},
                                                  {'$set': {'rating': rating, 'last_updated': datetime.datetime.utcnow()}},
                                                  upsert=True)
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

            self.finish()
        else:
            raise tornado.web.HTTPError(401)  # Unauthorized
