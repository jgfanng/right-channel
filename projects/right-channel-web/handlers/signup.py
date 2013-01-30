'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler

class SignupHandler(BaseHandler):
    def initialize(self):
        self.context = {'site_nav': 'signup'}

    def get(self):
        self.render('account/signup_page.html', context=self.context)
