'''
Created on Jan 21, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from handlers.base_handler import BaseHandler, user_profile
from settings import mongodb
import tornado.web

class MovieProfileHandler(BaseHandler):
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

        # If movie is playable, get all play links.
        if movie.get('playable'):
            try:
                result, error = yield tornado.gen.Task(mongodb['movie.play_links'].find,
                                                       spec={'movie_id': movie.get('_id')})
                self.params['play_links'] = result[0]
            except:
                raise tornado.web.HTTPError(500)
            if error.get('error'):
                raise tornado.web.HTTPError(500)

        # If user is logged in, get user interest and rating.
        user = self.params.get('user')
        if user:
            # set user interest: wish, dislike
            try:
                result, error = yield tornado.gen.Task(mongodb['movie.interests'].find_one,
                                                       {'user_id': user.get('_id'), 'movie_id': movie.get('_id')})
                if result[0]:
                    movie['user_interest'] = result[0].get('type')
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

            # set user rating
            try:
                result, error = yield tornado.gen.Task(mongodb['movie.ratings'].find_one,
                                                       {'user_id': user.get('_id'), 'movie_id': movie.get('_id')})
                if result[0]:
                    movie['user_rating'] = result[0].get('rating')
            except:
                raise tornado.web.HTTPError(500)
            if error.get('error'):
                raise tornado.web.HTTPError(500)

        self.params['movie'] = movie
        self.render('movie/movie_profile_page.html')
