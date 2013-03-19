'''
Created on Mar 13, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from settings import mongodb
from tornado.web import HTTPError
import tornado.gen
import tornado.web

class MovieIgnoredHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        email = self.get_secure_cookie('email')
        if email:
            # 400 Bad Request if id not provided
            movie_id = self.get_argument('id')

            # add movie to ignored list in accounts collection
            try:
                _, error = yield tornado.gen.Task(mongodb['accounts'].update,
                                                         {'email': email},
                                                         {'$addToSet': {'ignored.movie': ObjectId(movie_id)}})
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

            self.finish()
        else:
            raise HTTPError(401)  # Unauthorized

    @tornado.web.asynchronous
    @tornado.gen.engine
    def delete(self, movie_id):
        email = self.get_secure_cookie('email')
        if email:
            # remove movie from ignored list in accounts collection
            try:
                _, error = yield tornado.gen.Task(mongodb['accounts'].update,
                                                         {'email': email},
                                                         {'$pull': {'ignored.movie': ObjectId(movie_id)}})
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

            self.finish()
        else:
            raise HTTPError(401)  # Unauthorized
