'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
from handlers.default_handler import DefaultHandler
from handlers.home_handler import HomeHandler
from handlers.hot_movie_handler import HotMovieHandler
from handlers.movie_details_handler import MovieDetailsHandler
from handlers.new_movie_handler import NewMovieHandler
import os
import tornado.web

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
            (r'/movie', HotMovieHandler),
            (r'/movie/hot', HotMovieHandler),
            (r'/movie/new', NewMovieHandler),
            (r'/movie/([0-9a-f]{24})', MovieDetailsHandler),
            (r'/(.*)', DefaultHandler)
        ]
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            'template_path': os.path.join(os.path.dirname(__file__), "templates"),
            'debug': True
        }
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    Application().listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
