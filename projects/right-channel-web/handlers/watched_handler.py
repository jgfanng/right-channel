'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, authenticated_async
from settings import mongodb
import tornado.gen
import tornado.web

class WatchedHandler(BaseHandler):
    def initialize(self):
        super(WatchedHandler, self).initialize()
        self.params['site_nav'] = 'account'
        self.params['account_nav'] = 'watched'

    @authenticated_async
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        if self.params.get('user'):
            user = self.params.get('user')
            if user.get('watched') and user.get('watched').get('movie'):
                try:
                    response, error = yield tornado.gen.Task(mongodb['movies'].find,
                                                             {'_id': {'$in': user.get('watched').get('movie')}},
                                                             fields={'title': 1, 'original_title': 1, 'douban.rating': 1, 'year': 1})
                except:
                    raise tornado.web.HTTPError(500)

                if error.get('error'):
                    raise tornado.web.HTTPError(500)

                user['watched']['movie'] = response[0]

            self.params['user'] = user
            self.render('account/watched_page.html')
        else:
            self.set_cookie('next', '/account/watched', expires_days=None)  # Session cookie
            self.redirect('/login')
