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

class MovieRatingAPIHandler(BaseHandler):
    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self, movie_id):
        """Rate on a movie for current user.

        :URL path movie_id: Movie id.
        :post data rating: Movie rating (5.0 >= rating >= 0).

        This API need to be authorized.
        """
        user = self.params.get('user')
        if not user:
            raise tornado.web.HTTPError(401)  # Unauthorized

        user_id = user.get('_id')
        rating = self.get_argument('rating')
        try:
            rating = float(rating)
        except:
            raise tornado.web.HTTPError(400)
        if rating < 0 or rating > 5:
            raise tornado.web.HTTPError(400)

        try:
            _, error = yield tornado.gen.Task(mongodb['movie.ratings'].update,
                                              {'user_id': user_id, 'movie_id': ObjectId(movie_id)},
                                              {'$set': {'rating': rating, 'last_updated': datetime.datetime.utcnow()}},
                                              upsert=True)
        except:
            raise tornado.web.HTTPError(500)

        if error.get('error'):
            raise tornado.web.HTTPError(500)

        self.finish()
