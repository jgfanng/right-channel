'''
Created on Jan 10, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler
import tornado.web

class DefaultHandler(BaseHandler):
    def prepare(self):
        raise tornado.web.HTTPError(404)

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.finish({'message': 'Resource Not Found'})
