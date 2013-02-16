# -*- coding: utf-8 -*-
'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler
from settings import collections
from util import encrypt
import tornado

class RegisterHandler(BaseHandler):
    def initialize(self):
        super(RegisterHandler, self).initialize()
        self.params['site_nav'] = 'register'

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

        self.render('account/register_page.html')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        email = self.get_argument('email', None)
        password = self.get_argument('password', None)
        nick_name = self.get_argument('nick-name', None)
        if not email or not password or not nick_name:
            self.params['op_result'] = {'type': 'error', 'message': '尊敬的用户，您输入的邮箱、密码或昵称不合理，请重新输入'}
            self.render('account/register_page.html')
            return

        try:
            response, error = yield tornado.gen.Task(collections['accounts'].find_one,
                                                     {'email': email},
                                                     fields={'email': 1})
        except:
            raise tornado.web.HTTPError(500)

        if 'error' in error and error['error']:
            raise tornado.web.HTTPError(500)

        user = response[0]
        if user:
            self.params['op_result'] = {'type': 'error', 'message': '尊敬的用户，您输入的邮箱已被注册，请重新输入'}
            self.render('account/register_page.html')
        else:
            try:
                response, error = yield tornado.gen.Task(collections['accounts'].insert,
                                                         {'email': email, 'password': encrypt(password), 'nick_name': nick_name})
            except:
                raise tornado.web.HTTPError(500)

            if 'error' in error and error['error']:
                raise tornado.web.HTTPError(500)

            self.set_secure_cookie('email', email)
            self.redirect('/')
