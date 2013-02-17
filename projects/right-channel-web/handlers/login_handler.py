# -*- coding: utf-8 -*-
'''
Created on Feb 7, 2013

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
        self.params['site_nav'] = 'login'

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        email = self.get_secure_cookie('email')
        if email:
            try:
                response, error = yield tornado.gen.Task(collections['accounts'].find_one,
                                                         {'email': email},
                                                         fields={'email': 1, 'nick_name': 1})
            except:
                raise tornado.web.HTTPError(500)

            if 'error' in error and error['error']:
                raise tornado.web.HTTPError(500)

            user = response[0]
            if user:
                self.params['user'] = user
            else:
                self.clear_cookie('email')

        self.render('account/login_page.html')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        email = self.get_argument('email', None)
        password = self.get_argument('password', None)
        persistent_login = self.get_argument('persistent_login', 'false')
        if not email or not password:
            self.params['op_result'] = {'type': 'error', 'message': '尊敬的用户，您输入的邮箱或密码不正确，请重新输入'}
            self.render('account/login_page.html')
            return

        try:
            response, error = yield tornado.gen.Task(collections['accounts'].find_one,
                                                     {'email': email},
                                                     fields={'email': 1, 'nick_name': 1, 'password': 1})
        except:
            raise tornado.web.HTTPError(500)

        if 'error' in error and error['error']:
            raise tornado.web.HTTPError(500)

        user = response[0]
        if user:
            if user.get('password') == encrypt(password):
                if persistent_login == 'true':
                    self.set_secure_cookie('email', user['email'])  # Persistent cookie
                else:
                    self.set_secure_cookie('email', user['email'], expires_days=None)  # Session cookie
                next_page = self.get_secure_cookie('next')
                if next_page:
                    self.clear_cookie('next')  # !important
                    self.redirect(next_page)
                else:
                    self.redirect('/')
            else:
                self.params['op_result'] = {'type': 'error', 'message': '尊敬的用户，您输入的密码不正确，请重新输入'}
                self.render('account/login_page.html')
        else:
            self.params['op_result'] = {'type': 'error', 'message': '尊敬的用户，您输入的邮箱不存在，请重新输入'}
            self.render('account/login_page.html')
