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
        self.context['site_nav'] = 'register'

    def get(self):
        self.render('account/register_page.html', op_result=None)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        email = self.get_argument('email')
        response, error = yield tornado.gen.Task(collections['accounts'].find_one, {'email': email})

        if 'error' in error and error['error']:
            self.render('account/register_page.html', op_result={'type': 'error', 'message': '尊敬的用户，当前操作无法完成，请联系管理员'})
            return

        user = response[0]
        if user:  # already exists
            self.render('account/register_page.html', op_result={'type': 'error', 'message': '尊敬的用户，您输入的邮箱已被使用'})
            return

        password = self.get_argument('password')
        nick_name = self.get_argument('nick-name')
        response, error = yield tornado.gen.Task(collections['accounts'].insert, {'email': email, 'password': encrypt(password), 'nick-name': nick_name})

        if 'error' in error and error['error']:
            self.render('account/register_page.html', op_result={'type': 'error', 'message': '尊敬的用户，当前操作无法完成，请联系管理员'})
            return

        self.set_secure_cookie('email', email)
        self.redirect('/movie/onshow')
