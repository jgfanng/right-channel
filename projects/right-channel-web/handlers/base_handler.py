'''
Created on Jan 10, 2013

@author: Fang Jiaguo
'''
from settings import mongodb
import functools
import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('email')

    def initialize(self):
        self.params = {}

    def render(self, template_name, **kwargs):
        kwargs['params'] = self.params
        super(BaseHandler, self).render(template_name, **kwargs)

def authenticated_async(extra_fields=[]):
    def decorator(method):
        @functools.wraps(method)
        @tornado.web.asynchronous
        @tornado.gen.engine
        def wrapper(self, *args, **kwargs):
            email = self.get_secure_cookie('email')
            if email:
                try:
                    simple_fields = ['email', 'password', 'nick_name', 'avatar']
                    simple_fields.extend(extra_fields)
                    final_fields = {}
                    for field in simple_fields:
                        final_fields[field] = 1

                    response, error = yield tornado.gen.Task(mongodb['accounts'].find_one,
                                                             {'email': email},
                                                             fields=final_fields)
                except:
                    raise tornado.web.HTTPError(500)

                if error.get('error'):
                    raise tornado.web.HTTPError(500)

                user = response[0]
                if user:
                    self.params['user'] = user

            method(self, *args, **kwargs)

        return wrapper
    return decorator
