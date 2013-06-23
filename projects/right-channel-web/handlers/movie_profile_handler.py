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

        user = self.params.get('user')
        if user:
            # set user interest: wish, dislike
            user_id = user.get('_id')
            try:
                result, error = yield tornado.gen.Task(mongodb['movie.interests'].find_one,
                                                       {'user_id': user_id, 'movie_id': movie.get('_id')})
                if result[0]:
                    movie.setdefault('user', {})
                    movie['user']['interest'] = result[0].get('type')
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

            # set rating
            try:
                result, error = yield tornado.gen.Task(mongodb['movie.ratings'].find_one,
                                                       {'user_id': user_id, 'movie_id': movie.get('_id')})
                if result[0]:
                    movie.setdefault('user', {})
                    movie['user']['rating'] = result[0].get('rating')
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

        self.params['movie'] = movie
        self.render('movie/movie_profile_page.html')
