'''
Created on Jan 9, 2013

@author: Fang Jiaguo
'''
from default_handler import DefaultHandler
from movie_handler import MovieHandler
import asyncmongo
import json
import tornado.web

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/movies/movie-([0-9a-f]{24})', MovieHandler),
            (r'/movies/(year-.+)|(type-.+)', MovieHandler),
#            (r'/movies/year-(.+)/type-(.+)/country-(.+)', MoviesHandler),
#            (r'/movies/year-(.+)/type-(.+)/country-(.+)', MoviesHandler),
#            (r'/movies/year-(.+)/type-(.+)/country-(.+)', MoviesHandler),
#            (r'/movies/year-(.+)/type-(.+)/country-(.+)', MoviesHandler),
#            (r'/movies/year-(.+)/type-(.+)/country-(.+)', MoviesHandler),
#            (r'/movies/year-(.+)/type-(.+)/country-(.+)', MoviesHandler),
#            (r'/movies/year-(.+)/type-(.+)/country-(.+)', MoviesHandler),
            (r'/(.*)', DefaultHandler)
            ]
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)

        self.config = json.load(open('api-server.json', 'r'))
        self.mongodb = asyncmongo.Client(
            pool_id=self.config['mongo']['asyncmongo_pool_id'],
            host=self.config['mongo']['host'],
            port=self.config['mongo']['port'],
            dbname=self.config['mongo']['db'])

def main():
    Application().listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
