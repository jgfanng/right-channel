'''
Created on Mar 13, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from settings import mongodb
from tornado.web import HTTPError
import tornado.gen
import tornado.web

class MovieToUnwatchHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def delete(self, movie_id):
        email = self.get_secure_cookie('email')
        if email:
            # remove movie from to_watch list in accounts collection
            try:
                _, error = yield tornado.gen.Task(mongodb['accounts'].update,
                                                         {'email': email},
                                                         {'$pull': {'to_watch.movie': {'id': ObjectId(movie_id)}}})
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

            self.finish()
        else:
            raise HTTPError(401)  # Unauthorized
