'''
Created on Jan 9, 2013

@author: Fang Jiaguo
'''
from handlers.default_handler import DefaultHandler
from handlers.hot_handler import HotHandler
from handlers.movie_handler import MovieHandler
from handlers.movies_handler import MoviesHandler
import tornado.web

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/movies/([0-9a-f]{24})', MovieHandler),
            (r'/movies', MoviesHandler),
            (r'/movies/hot-(week|month|history)', HotHandler),
            (r'/(.*)', DefaultHandler)
            ]
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    Application().listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
