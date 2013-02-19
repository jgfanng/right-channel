'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, get_current_user_info
from settings import collections, settings
import tornado.gen
import tornado.web

class WatchedHandler(BaseHandler):
    def initialize(self):
        super(WatchedHandler, self).initialize()
        self.params['site_nav'] = 'account'
        self.params['account_nav'] = 'watched'

    @get_current_user_info(extra_fields=['watched.movie'])
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        if self.params.get('user'):
            user = self.params.get('user')
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
            self.set_secure_cookie('next', '/account/watched', expires_days=None)  # Session cookie
            self.redirect('/login')
