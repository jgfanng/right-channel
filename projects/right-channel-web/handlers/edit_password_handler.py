'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler

class EditPasswordHandler(BaseHandler):
    def initialize(self):
        super(EditPasswordHandler, self).initialize()
        self.context['site_nav'] = 'account'
        self.context['account_nav'] = 'editpassword'

    def get(self):
        self.render('account/edit_password.html')
