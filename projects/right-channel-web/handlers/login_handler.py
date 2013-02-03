'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler
from settings import collections
import hashlib
import tornado

class LoginHandler(BaseHandler):
    def initialize(self):
        self.context = {'site_nav': 'login'}

    def get(self):
        self.render('account/login_page.html', context=self.context)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        email = self.get_argument('email')
        password = self.get_argument('password')

        user, error = yield tornado.gen.Task(collections['accounts'].find_one, {'email': email})
        if user:
            if 'password' in user and user['password'] == hashlib.sha256(password).digest():
                self.set_current_user(email)
                self.redirect('/movie/onshow')
