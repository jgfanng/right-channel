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
    def initialize(self):
        self.context = {}

    def render(self, template_name, **kwargs):
        kwargs['context'] = self.context
        kwargs['email'] = self.get_secure_cookie('email')
        super(BaseHandler, self).render(template_name, **kwargs)
