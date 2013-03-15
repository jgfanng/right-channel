'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, authenticated_async
import tornado.gen
import tornado.web

class WatchedHandler(BaseHandler):
    def initialize(self):
        super(WatchedHandler, self).initialize()
        self.params['site_nav'] = 'account'
        self.params['account_nav'] = 'watched'

    @authenticated_async(extra_fields=['watched.movie'])
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        if self.params.get('user'):
            self.render('account/watched_page.html')
        else:
            self.set_cookie('next', '/account/watched', expires_days=None)  # Session cookie
            self.redirect('/login')
