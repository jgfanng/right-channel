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

    def get(self):
        self.render('account/login_page.html')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        email = self.get_argument('email', None)
        password = self.get_argument('password', None)
        persistent_login = self.get_argument('persistent_login', 'false')
        if not email or not password:
            self.params['op_result'] = {'type': 'error', 'message': '尊敬的用户，您输入的邮箱或密码不合理，请重新输入'}
            self.render('account/login_page.html')
            return

        response, error = yield tornado.gen.Task(collections['accounts'].find_one,
                                                 {'email': email},
                                                 fields={'email': 1, 'password': 1, 'nick_name': 1})

        if 'error' in error and error['error']:
            self.params['op_result'] = {'type': 'error', 'message': '尊敬的用户，当前操作无法完成，请联系管理员'}
            self.render('account/login_page.html')
            return

        user = response[0]
        if user:
            if user.get('password') == encrypt(password):
                if persistent_login == 'true':
                    self.set_secure_cookie('email', user['email'])  # Persistent cookie
                else:
                    self.set_secure_cookie('email', user['email'], expires_days=None)  # Session cookie
                next_page = self.get_secure_cookie('next')
                self.clear_cookie('next')
                self.redirect(next_page or '/')
                return
            else:
                self.params['op_result'] = {'type': 'error', 'message': '尊敬的用户，您输入的密码不正确，请重新输入'}
                self.render('account/login_page.html')
                return
        else:
            self.params['op_result'] = {'type': 'error', 'message': '尊敬的用户，您输入的邮箱不存在，请重新输入'}
            self.render('account/login_page.html')
            return
