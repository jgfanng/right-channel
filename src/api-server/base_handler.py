'''
Created on Jan 10, 2013

@author: Fang Jiaguo
'''
import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    @property
    def mongodb(self):
        return self.application.mongodb

    # disable tornado's default etag computation
    def compute_etag(self):
        return None
