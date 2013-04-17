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
            response, error = yield tornado.gen.Task(mongodb['movies'].find_one,
                                                     {'_id': ObjectId(movie_id)})
        except:
            raise tornado.web.HTTPError(500)

        if error.get('error'):
            raise tornado.web.HTTPError(500)

        # 404 not found if no movie found
        movie = response[0]
        if not movie:  # None or []
            raise tornado.web.HTTPError(404)

        # set to_watch, watched and not_interested status
        user = self.params.get('user')
        if user and user.get('to_watch') and user.get('to_watch').get('movie'):
            if movie.get('_id') in user.get('to_watch').get('movie'):
                movie['to_watch'] = True
            else:
                movie['to_watch'] = False

        if user and user.get('watched') and user.get('watched').get('movie'):
            if movie.get('_id') in user.get('watched').get('movie'):
                movie['watched'] = True
            else:
                movie['watched'] = False

        if user and user.get('not_interested') and user.get('not_interested').get('movie'):
            if movie.get('_id') in user.get('not_interested').get('movie'):
                movie['not_interested'] = True
            else:
                movie['not_interested'] = False

        self.params['movie'] = movie
        self.render('movie/movie_profile_page.html')
