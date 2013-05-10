'''
Created on Mar 13, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from handlers.base_handler import BaseHandler, user_profile
from settings import mongodb
from tornado.web import HTTPError
import datetime
import tornado.gen
import tornado.web

class MovieUserBehaviorHandler(BaseHandler):
    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        user = self.params.get('user')
        if user:
            user_id = user.get('_id')
            movie_id = self.get_argument('movie_id')
            behavior_type = self.get_argument('behavior_type')
            if behavior_type not in ['to_watch', 'watched', 'not_interested']:
                raise HTTPError(400)

            try:
                _, error = yield tornado.gen.Task(mongodb['user_behaviors'].update,
                                                  {'user_id': user_id, 'movie_id': ObjectId(movie_id)},
                                                  {'$set': {'behavior_type': behavior_type, 'last_updated': datetime.datetime.utcnow()}},
                                                  upsert=True)
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

            self.finish()
        else:
            raise HTTPError(401)  # Unauthorized

    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def delete(self, movie_id):
        user = self.params.get('user')
        if user:
            try:
                user_id = user.get('_id')
                _, error = yield tornado.gen.Task(mongodb['user_behaviors'].update,
                                                  {'user_id': user_id, 'movie_id': ObjectId(movie_id)},
                                                  {'$unset': {'behavior_type': ''}, '$set': {'last_updated': datetime.datetime.utcnow()}})
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

            self.finish()
        else:
            raise HTTPError(401)  # Unauthorized
