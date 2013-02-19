# -*- coding: utf-8 -*-
'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, get_current_user_info
from settings import collections
from util import encrypt
import tornado

class RegisterHandler(BaseHandler):
    def initialize(self):
        super(RegisterHandler, self).initialize()
        self.params['site_nav'] = 'register'

    @get_current_user_info()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.render('account/register_page.html')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        email = self.get_argument('email', None)
        password = self.get_argument('password', None)
        nick_name = self.get_argument('nick-name', None)
        if not email or not password or not nick_name:
            self.params['op_result'] = {'type': 'error', 'message': '您输入的邮箱、密码或昵称不正确，请重新输入'}
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
            self.params['op_result'] = {'type': 'error', 'message': '您输入的邮箱已被注册，请重新输入'}
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
