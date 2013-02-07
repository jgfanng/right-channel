'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler
from settings import collections
import tornado.gen
import tornado.web

class EditProfileHandler(BaseHandler):
    def initialize(self):
        super(EditProfileHandler, self).initialize()
        self.params['site_nav'] = 'account'
        self.params['account_nav'] = 'editprofile'

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        email = self.get_secure_cookie('email')
        if email:
            response, error = yield tornado.gen.Task(collections['accounts'].find_one,
                                                     {'email': email},
                                                     fields={'email': 1, 'nick_name': 1})

            if 'error' in error and error['error'] and not response[0]:
                self.clear_cookie('email')
                self.redirect('/')
                return

            self.params['user'] = response[0]

        self.render('account/edit_profile_page.html')
