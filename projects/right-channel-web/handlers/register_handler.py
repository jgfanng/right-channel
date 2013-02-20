# -*- coding: utf-8 -*-
'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, authenticated_async
from settings import collections, email_regex
from util import encrypt
import tornado

class RegisterHandler(BaseHandler):
    def initialize(self):
        super(RegisterHandler, self).initialize()
        self.params['site_nav'] = 'register'

    @authenticated_async()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.render('account/register_page.html')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        email = self.get_argument('email', '').strip()
        password = self.get_argument('password', '')
        nick_name = self.get_argument('nick-name', '').strip()

        if (0 < len(email) <= 254 and email_regex.match(email) and
            6 <= len(password) <= 16 and 0 < len(nick_name) <= 12):
            try:
                # here we use insert to ensure concurrency
                _, error = yield tornado.gen.Task(collections['accounts'].insert,
                                                  {'email': email, 'password': encrypt(password), 'nick_name': nick_name})
            except:
                raise tornado.web.HTTPError(500)

            # Code 11000: duplicate key error
            if error.get('error'):
                if error.get('error').code == 11000:
                    self.params['op_result'] = {'type': 'error', 'message': '您输入的邮箱已被注册，请重新输入'}
                    self.render('account/register_page.html')
                else:
                    raise tornado.web.HTTPError(500)
            else:
                self.set_secure_cookie('email', email)
                self.redirect('/')
        else:
            raise tornado.web.HTTPError(403)
