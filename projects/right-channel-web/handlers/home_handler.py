'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, user_profile
from settings import mongodb
import tornado.gen
import tornado.web

class HomeHandler(BaseHandler):

    NEWEST_MOVIES = 30
    HOTEST_MOVIES = 60

    def initialize(self):
        self.params['site_nav'] = '/'

    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        # Newest movies
        try:
            result, error = yield tornado.gen.Task(mongodb['movies'].find,
                                                   fields={'summary': 0},
                                                   limit=self.NEWEST_MOVIES,
                                                   sort=[('available_at', -1)])
        except:
            raise tornado.web.HTTPError(500)
        if error.get('error'):
            raise tornado.web.HTTPError(500)

        self.params['newest_movies'] = result[0]

        # Hottest movies
        try:
            result, error = yield tornado.gen.Task(mongodb['movies'].find,
                                                   spec={'is_movie': True},
                                                   fields={'summary': 0},
                                                   limit=self.HOTEST_MOVIES,
                                                   sort=[('hits', -1)])
        except:
            raise tornado.web.HTTPError(500)
        if error.get('error'):
            raise tornado.web.HTTPError(500)

        self.params['hottest_movies'] = result[0]
        # Hottest TV serials
        self.render('index.html')
