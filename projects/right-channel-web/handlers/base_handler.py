'''
Created on Jan 10, 2013

@author: Fang Jiaguo
'''
from settings import mongodb
import functools
import tornado.web

class BaseHandler(tornado.web.RequestHandler):

    MOVIES_PER_REQUEST = 30
    TOTAL_ACCESSABLE_MOVIES = 1000
    SORT_FIELDS = ['available_at', 'hits']

    def __init__(self, application, request, **kwargs):
        self.params = {}
        super(BaseHandler, self).__init__(application, request, **kwargs)

    def get_current_user(self):
        return self.get_secure_cookie('email')

    def render(self, template_name, **kwargs):
        kwargs['params'] = self.params
        super(BaseHandler, self).render(template_name, **kwargs)

def user_profile(method):
    @functools.wraps(method)
    @tornado.web.asynchronous
    @tornado.gen.engine
    def wrapper(self, *args, **kwargs):
        email = self.get_secure_cookie('email')
        if email:
            try:
                response, error = yield tornado.gen.Task(mongodb['accounts'].find_one,
                                                         {'email': email})
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

            if response[0]:
                self.params['user'] = response[0]

        method(self, *args, **kwargs)

    return wrapper
