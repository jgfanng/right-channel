'''
Created on Jan 9, 2013

@author: Fang Jiaguo
'''
from base_handler import BaseHandler
from bson.objectid import ObjectId
from utils.json_encoder_ext import JSONEncoderExt
import json
import tornado.web

class MovieHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, movie_id):
        self.mongodb['movies'].find_one(
            {'_id': ObjectId(movie_id)},
            fields={'year': 1,
                    'title': 1,
                    'alt_titles': 1,
                    'directors': 1,
                    'writers': 1,
                    'casts': 1,
                    'types': 1,
                    'countries': 1,
                    'languages': 1,
                    'pubdates': 1,
                    'durations': 1,
                    'image': 1,
                    'summary': 1,
                    'douban_id': 1,
                    'douban_rating': 1,
                    'imdb_id': 1,
                    'imdb_rating': 1,
                    'sources': 1},
            callback=self._on_response)

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.finish({'message': 'Movie Not Found'})
        elif status_code == 500:
            self.finish({'message': 'Internal Server Error'})
        else:
            super(MovieHandler, self).write_error(status_code, **kwargs)

    def _on_response(self, response, error):
        if error:
            raise tornado.web.HTTPError(500)
        if not response:
            raise tornado.web.HTTPError(404)

        if '_id' in response:
            response['id'] = response.pop('_id')
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(response, cls=JSONEncoderExt))
        self.finish()
