'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, get_current_user_info
import tornado.gen
import tornado.web

class EditProfileHandler(BaseHandler):
    def initialize(self):
        super(EditProfileHandler, self).initialize()
        self.params['site_nav'] = 'account'
        self.params['account_nav'] = 'editprofile'

    @get_current_user_info()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        if self.params.get('user'):
            self.render('account/edit_profile_page.html')
        else:
            self.set_secure_cookie('next', '/account/editprofile', expires_days=None)  # Session cookie
            self.redirect('/login')
