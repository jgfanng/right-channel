'''
Created on Jan 9, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from handlers.base_handler import BaseHandler
from utils.json_encoder_ext import JSONEncoderExt
from utils.settings import collections, settings
import json
import tornado.web

class MovieHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, movie_id):
        collections['movies'].find_one(
            {'_id': ObjectId(movie_id)},
            fields=settings['movie']['response']['verbose'],
            callback=self._on_response)

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.finish({'message': 'Movie not found'})
        else:
            super(MovieHandler, self).write_error(status_code, **kwargs)

    def _on_response(self, response, error):
        if error:
            raise tornado.web.HTTPError(500)
        if not response:
            raise tornado.web.HTTPError(404)

        response['id'] = response.pop('_id')
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(response, cls=JSONEncoderExt))
        self.finish()
