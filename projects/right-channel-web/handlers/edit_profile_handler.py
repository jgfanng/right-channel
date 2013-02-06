'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler

class EditProfileHandler(BaseHandler):
    def initialize(self):
        super(EditProfileHandler, self).initialize()
        self.context['site_nav'] = 'account'
        self.context['account_nav'] = 'editprofile'

    def get(self):
        self.render('account/edit_profile.html')
