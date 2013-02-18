'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler
from settings import collections, settings
import tornado.gen
import tornado.web

class ToWatchHandler(BaseHandler):
    def initialize(self):
        super(ToWatchHandler, self).initialize()
        self.params['site_nav'] = 'account'
        self.params['account_nav'] = 'towatch'

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        email = self.get_secure_cookie('email')
        if email:
            try:
                response, error = yield tornado.gen.Task(collections['accounts'].find_one,
                                                         {'email': email},
                                                         fields={'email': 1, 'nick_name': 1, 'to_watch': 1})
            except:
                raise tornado.web.HTTPError(500)

            if 'error' in error and error['error']:
                raise tornado.web.HTTPError(500)

            user = response[0]
            if user:
                if user.get('to_watch') and user.get('to_watch').get('movie'):
                    try:
                        response, error = yield tornado.gen.Task(collections['movies'].find,
                                                                 {'_id': {'$in': user.get('to_watch').get('movie')}},
                                                                 fields=settings['movie']['response']['verbose'])
                    except:
                        raise tornado.web.HTTPError(500)

                    if 'error' in error and error['error']:
                        raise tornado.web.HTTPError(500)

                    user['to_watch']['movie'] = response[0]

                self.params['user'] = user
                self.render('account/to_watch_page.html')
            else:
                self.clear_cookie('email')
                self.set_secure_cookie('next', '/account/towatch', expires_days=None)  # Session cookie
                self.redirect('/login')
        else:
            self.set_secure_cookie('next', '/account/towatch', expires_days=None)  # Session cookie
            self.redirect('/login')
