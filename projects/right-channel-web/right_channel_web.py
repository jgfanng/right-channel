'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.default_handler import DefaultHandler
from handlers.home_handler import HomeHandler
from handlers.hot_movie_handler import HotMovieHandler
from handlers.login_handler import LoginHandler
from handlers.movie_details_handler import MovieDetailsHandler
from handlers.onshow_movie_handler import OnshowMovieHandler
from handlers.register_handler import RegisterHandler
import base64
import os
import tornado.web
import uuid

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
            (r'/movie', HotMovieHandler),
            (r'/movie/hot', HotMovieHandler),
            (r'/movie/onshow', OnshowMovieHandler),
            (r'/movie/([0-9a-f]{24})', MovieDetailsHandler),
            (r'/login', LoginHandler),
            (r'/register', RegisterHandler),
            (r'/(.*)', DefaultHandler)
        ]
        settings = {
            'debug': True,
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            'xsrf_cookies': True,
            'cookie_secret': base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            'login_url': "/login"
        }
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    Application().listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
