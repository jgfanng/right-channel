'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler

class RegisterHandler(BaseHandler):
    def initialize(self):
        self.context = {'site_nav': 'register'}

    def get(self):
        self.render('account/register_page.html', context=self.context)
