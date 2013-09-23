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

class MovieInterestAPIHandler(BaseHandler):
    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self, movie_id):
        """Set interest on a movie for current user.

        :URL path movie_id: Movie id.
        :post data type: Interest type ('wish', 'dislike').

        This API need to be authorized.
        """
        user = self.params.get('user')
        if not user:
            raise tornado.web.HTTPError(401)  # Unauthorized

        user_id = user.get('_id')
        interest_type = self.get_argument('type')
        if interest_type not in ['wish', 'dislike']:
            raise tornado.web.HTTPError(400)  # Bad Request

        try:
            _, error = yield tornado.gen.Task(mongodb['movie.interests'].update,
                                              {'user_id': user_id, 'movie_id': ObjectId(movie_id)},
                                              {'$set': {'type': interest_type, 'last_updated': datetime.datetime.utcnow()}},
                                              upsert=True)
        except:
            raise tornado.web.HTTPError(500)
        if error.get('error'):
            raise tornado.web.HTTPError(500)

        self.finish()

    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def delete(self, movie_id):
        """Delete interest on a movie for current user.

        :URL path movie_id: Movie id.

        This API need to be authorized.
        """
        user = self.params.get('user')
        if not user:
            raise tornado.web.HTTPError(401)  # Unauthorized

        user_id = user.get('_id')
        try:
            _, error = yield tornado.gen.Task(mongodb['movie.interests'].remove,
                                              {'user_id': user_id, 'movie_id': ObjectId(movie_id)})
        except:
            raise tornado.web.HTTPError(500)
        if error.get('error'):
            raise tornado.web.HTTPError(500)

        self.finish()
