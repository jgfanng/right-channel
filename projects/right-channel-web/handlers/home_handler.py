'''
Created on Jan 16, 2013

@author: Fang Jiaguo
'''
import tornado.web

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
