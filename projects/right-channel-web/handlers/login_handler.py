'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler
from settings import collections
from util import encrypt
import tornado.gen
import tornado.web

class LoginHandler(BaseHandler):
    def initialize(self):
        super(LoginHandler, self).initialize()
        self.context['site_nav'] = 'login'

    def get(self):
        self.render('account/login_page.html')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        email = self.get_argument('email')
        password = self.get_argument('password')
        persistent_login = self.get_argument('persistent_login', 'false')

        response, error = yield tornado.gen.Task(collections['accounts'].find_one, {'email': email})
        user = response[0]
        if user and 'password' in user and user['password'] == encrypt(password):
            if persistent_login == 'true':
                self.set_secure_cookie('email', user['email'])  # Persistent cookies
            else:
                self.set_secure_cookie('email', user['email'], expires_days=None)  # Session cookies: erased on browser close.
            self.redirect('/movie/onshow')
        else:
            self.redirect('/login')
