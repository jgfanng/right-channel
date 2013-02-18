'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler
from settings import collections, settings
import tornado.gen
import tornado.web

class WatchedHandler(BaseHandler):
    def initialize(self):
        super(WatchedHandler, self).initialize()
        self.params['site_nav'] = 'account'
        self.params['account_nav'] = 'watched'

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        email = self.get_secure_cookie('email')
        if email:
            try:
                response, error = yield tornado.gen.Task(collections['accounts'].find_one,
                                                         {'email': email},
                                                         fields={'email': 1, 'nick_name': 1, 'watched': 1})
            except:
                raise tornado.web.HTTPError(500)

            if 'error' in error and error['error']:
                raise tornado.web.HTTPError(500)

            user = response[0]
            if user:
                if user.get('watched') and user.get('watched').get('movie'):
                    try:
                        response, error = yield tornado.gen.Task(collections['movies'].find,
                                                                 {'_id': {'$in': user.get('watched').get('movie')}},
                                                                 fields=settings['movie']['response']['verbose'])
                    except:
                        raise tornado.web.HTTPError(500)

                    if 'error' in error and error['error']:
                        raise tornado.web.HTTPError(500)

                    user['watched']['movie'] = response[0]

                self.params['user'] = user
                self.render('account/watched_page.html')
            else:
                self.clear_cookie('email')
                self.set_secure_cookie('next', '/account/watched', expires_days=None)  # Session cookie
                self.redirect('/login')
        else:
            self.set_secure_cookie('next', '/account/watched', expires_days=None)  # Session cookie
            self.redirect('/login')
