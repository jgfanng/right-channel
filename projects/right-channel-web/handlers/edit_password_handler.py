# -*- coding: utf-8 -*-
'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, authenticated_async
from settings import mongodb
from util import encrypt
import tornado.gen
import tornado.web

class EditPasswordHandler(BaseHandler):
    def initialize(self):
        super(EditPasswordHandler, self).initialize()
        self.params['site_nav'] = 'account'
        self.params['account_nav'] = 'editpassword'

    @authenticated_async()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        if self.params.get('user'):
            self.render('account/edit_password_page.html')
        else:
            self.set_secure_cookie('next', '/account/editpassword', expires_days=None)  # Session cookie
            self.redirect('/login')

    @authenticated_async()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        if self.params.get('user'):
            password_in_db = self.params.get('user').get('password')
            # throw an HTTP 400 exception if missing
            old_password = self.get_argument('old-password')
            new_password = self.get_argument('new-password')
            if 6 <= len(old_password) <= 16 and 6 <= len(new_password) <= 16:
                # the password from user input must be the same with the one in DB
                if password_in_db == encrypt(old_password):
                    try:
                        _, error = yield tornado.gen.Task(mongodb['accounts'].update,
                                                                 {'email': self.params.get('user').get('email')},
                                                                 {'$set': {'password': encrypt(new_password)}})
                    except:
                        raise tornado.web.HTTPError(500)

                    if error.get('error'):
                        raise tornado.web.HTTPError(500)

                    self.params['op_result'] = {'type': 'success', 'message': '密码更新成功'}
                    self.render('account/edit_password_page.html')
                else:
                    self.params['op_result'] = {'type': 'error', 'message': '您输入的旧密码不正确，请重新输入'}
                    self.render('account/edit_password_page.html')
            else:
                raise tornado.web.HTTPError(403)
        else:
            raise tornado.web.HTTPError(403)
