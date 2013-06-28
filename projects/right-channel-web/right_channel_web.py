'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from apis.movie_filter_api_handler import MovieFilterAPIHandler
from apis.movie_interest_api_handler import MovieInterestAPIHandler
from apis.movie_rating_api_handler import MovieRatingAPIHandler
from apis.movie_rating_candidate_api_handler import \
    MovieRatingCandidateAPIHandler
from apis.movie_rcmd_api_handler import MovieRcmdAPIHandler
from handlers.default_handler import DefaultHandler
from handlers.edit_password_handler import EditPasswordHandler
from handlers.edit_profile_handler import EditProfileHandler
from handlers.home_handler import HomeHandler
from handlers.hot_movie_handler import HotMovieHandler
from handlers.login_handler import LoginHandler
from handlers.logout_handler import LogoutHandler
from handlers.movie_category_handler import MovieCategoryHandler
from handlers.movie_profile_handler import MovieProfileHandler
from handlers.movie_rating_handler import MovieRatingHandler
from handlers.movie_recommendation_handler import MovieRecommendationHandler
from handlers.register_handler import RegisterHandler
from handlers.to_watch_handler import ToWatchHandler
from handlers.watched_handler import WatchedHandler
import os
import tornado.web

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
            (r'/movie/recommendation', MovieRecommendationHandler),
            (r'/movie/rating', MovieRatingHandler),
            (r'/movie', MovieCategoryHandler),
            (r'/movie/hot', HotMovieHandler),
            (r'/movie/([0-9a-f]{24})', MovieProfileHandler),
            (r'/account', ToWatchHandler),
            (r'/account/towatch', ToWatchHandler),
            (r'/account/watched', WatchedHandler),
            (r'/account/editprofile', EditProfileHandler),
            (r'/account/editpassword', EditPasswordHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/register', RegisterHandler),
            (r'/api/movie', MovieFilterAPIHandler),
            (r'/api/movie/([0-9a-f]{24})/interest', MovieInterestAPIHandler),
            (r'/api/movie/([0-9a-f]{24})/rating', MovieRatingAPIHandler),
            (r'/api/movie/recommendation', MovieRcmdAPIHandler),
            (r'/api/movie/rating-candidate', MovieRatingCandidateAPIHandler),
            (r'/(.*)', DefaultHandler)
        ]
        settings = {
            'debug': True,
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            'cookie_secret': 'B37kopZLQFSSqM1vTIeLEGWOTC/3yUiPl9Az+WlZV+A=',
            'login_url': "/login"
        }
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    Application().listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
