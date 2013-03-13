'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, authenticated_async
import tornado.gen
import tornado.web

class ToWatchHandler(BaseHandler):
    def initialize(self):
        super(ToWatchHandler, self).initialize()
        self.params['site_nav'] = 'account'
        self.params['account_nav'] = 'towatch'

    @authenticated_async(extra_fields=['to_watch.movie'])
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        if self.params.get('user'):
            self.render('account/to_watch_page.html')
        else:
            self.set_secure_cookie('next', '/account/towatch', expires_days=None)  # Session cookie
            self.redirect('/login')
