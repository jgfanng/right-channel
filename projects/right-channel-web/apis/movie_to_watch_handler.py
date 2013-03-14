'''
Created on Mar 13, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from settings import mongodb
from tornado.web import HTTPError
import tornado.gen
import tornado.web

class MovieToWatchHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        # TODO: xsrf_cookies needed (bug)
        email = self.get_secure_cookie('email')
        if email:
            movie_id = self.get_argument('id')  # must provide
            try:
                response, error = yield tornado.gen.Task(mongodb['movies'].find_one,
                                                         {'_id': ObjectId(movie_id)},
                                                         fields={'title': 1, 'original_title': 1, 'year': 1})
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

            if response[0]:
                movie = response[0]
                movie['id'] = movie.pop('_id')
            else:  # the cookied user not found in DB
                raise tornado.web.HTTPError(500)

            try:
                response, error = yield tornado.gen.Task(mongodb['accounts'].update,
                                                         {'email': email},
                                                         {'$addToSet': {'to_watch.movie': movie}})
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

            self.finish()
        else:
            raise HTTPError(401)
