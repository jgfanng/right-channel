'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, authenticated_async
from settings import collections, settings
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
            user = self.params.get('user')
            if user.get('to_watch') and user.get('to_watch').get('movie'):
                try:
                    response, error = yield tornado.gen.Task(collections['movies'].find,
                                                             {'_id': {'$in': user.get('to_watch').get('movie')}},
                                                             fields=settings['movie']['response']['verbose'])
                except:
                    raise tornado.web.HTTPError(500)

                if error.get('error'):
                    raise tornado.web.HTTPError(500)

                user['to_watch']['movie'] = response[0]

            self.params['user'] = user
            self.render('account/to_watch_page.html')
        else:
            self.set_secure_cookie('next', '/account/towatch', expires_days=None)  # Session cookie
            self.redirect('/login')
