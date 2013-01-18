'''
Created on Jan 10, 2013

@author: Fang Jiaguo
'''
import tornado.web

TEXT_FORMAT = 'text'
IMAGE_TEXT_FORMAT = 'image-text'
IMAGE_FORMAT = 'image'
VIEW_FORMATS = [TEXT_FORMAT, IMAGE_TEXT_FORMAT, IMAGE_FORMAT]

class BaseHandler(tornado.web.RequestHandler):
    # disable tornado's default etag computation
    def compute_etag(self):
        return None
