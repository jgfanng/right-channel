'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('email')
        self.redirect('/movie/onshow')
