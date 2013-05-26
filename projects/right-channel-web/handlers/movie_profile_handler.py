'''
Created on Jan 21, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from handlers.base_handler import BaseHandler, user_profile
from settings import mongodb
import tornado.web

class MovieProfileHandler(BaseHandler):
    def initialize(self):
        self.params['site_nav'] = 'movie'

    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, movie_id):
        try:
            result, error = yield tornado.gen.Task(mongodb['movies'].find_one,
                                                   {'_id': ObjectId(movie_id)})
        except:
            raise tornado.web.HTTPError(500)

        if error.get('error'):
            raise tornado.web.HTTPError(500)

        # 404 not found if no movie found
        movie = result[0]
        if not movie:  # None or []
            raise tornado.web.HTTPError(404)

        # set user behaviors: to_watch, watched and not_interested
        user = self.params.get('user')
        if user and movie:
            try:
                user_id = user.get('_id')
                result, error = yield tornado.gen.Task(mongodb['interests'].find_one,
                                                       {'user_id': user_id, 'movie_id': movie.get('_id')})
                if result[0]:
                    movie['user_interest'] = result[0].get('type')
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

            try:
                user_id = user.get('_id')
                result, error = yield tornado.gen.Task(mongodb['ratings'].find_one,
                                                       {'user_id': user_id, 'movie_id': movie.get('_id')})
                if result[0]:
                    movie['user_rating'] = result[0].get('rating')
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

        self.params['movie'] = movie
        self.render('movie/movie_profile_page.html')
