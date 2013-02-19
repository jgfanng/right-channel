'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, authenticated_async
import tornado.gen
import tornado.web

class EditProfileHandler(BaseHandler):
    def initialize(self):
        super(EditProfileHandler, self).initialize()
        self.params['site_nav'] = 'account'
        self.params['account_nav'] = 'editprofile'

    @authenticated_async()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        if self.params.get('user'):
            self.render('account/edit_profile_page.html')
        else:
            self.set_secure_cookie('next', '/account/editprofile', expires_days=None)  # Session cookie
            self.redirect('/login')
