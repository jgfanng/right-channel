'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler

class LoginHandler(BaseHandler):
    def initialize(self):
        self.context = {'site_nav': 'login'}

    def get(self):
        self.render('account/login_page.html', context=self.context)
