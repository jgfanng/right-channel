# -*- coding: utf-8 -*-
'''
Created on Jan 30, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, authenticated_async
from settings import collections
import tornado.gen
import tornado.web

class EditProfileHandler(BaseHandler):
    def initialize(self):
        super(EditProfileHandler, self).initialize()
        self.params['site_nav'] = 'account'
        self.params['account_nav'] = 'editprofile'

    @authenticated_async()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        if self.params.get('user'):
            self.render('account/edit_profile_page.html')
        else:
            self.set_secure_cookie('next', '/account/editprofile', expires_days=None)  # Session cookie
            self.redirect('/login')

    @authenticated_async()
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        if self.params.get('user'):
            # throw an HTTP 400 exception if missing
            nick_name = self.get_argument('nick-name')
            if 0 < len(nick_name) <= 12:
                try:
                    _, error = yield tornado.gen.Task(collections['accounts'].update,
                                                      {'email': self.params.get('user').get('email')},
                                                      {'$set': {'nick_name': nick_name}})
                except:
                    raise tornado.web.HTTPError(500)

                if error.get('error'):
                    raise tornado.web.HTTPError(500)

                self.params['user']['nick_name'] = nick_name  # display new nick name on page
                self.params['op_result'] = {'type': 'success', 'message': '个人资料更新成功'}
                self.render('account/edit_profile_page.html')
            else:
                raise tornado.web.HTTPError(403)
        else:
            raise tornado.web.HTTPError(403)
