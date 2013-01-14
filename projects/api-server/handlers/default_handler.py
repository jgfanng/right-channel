'''
Created on Jan 10, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler
import tornado.web

class DefaultHandler(BaseHandler):
    def head(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)

    def get(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)

    def post(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)

    def delete(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)

    def patch(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)

    def put(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)

    def options(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.finish({'message': 'Resource Not Found'})
