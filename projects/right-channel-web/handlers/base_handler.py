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
    def get_current_user(self):
        return self.get_secure_cookie('email')

    def initialize(self):
        self.params = {}

    def render(self, template_name, **kwargs):
        kwargs['params'] = self.params
        super(BaseHandler, self).render(template_name, **kwargs)
