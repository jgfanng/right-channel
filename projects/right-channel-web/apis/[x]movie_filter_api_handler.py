# -*- coding: utf-8 -*-
'''
Created on Mar 11, 2013

@author: Fang Jiaguo
'''
from handlers.base_handler import BaseHandler, user_profile
from settings import settings, mongodb
from utilities import first_element, last_element, get_body, JSONEncoderExt
import json
import tornado.gen
import tornado.web

class MovieFilterAPIHandler(BaseHandler):
    @user_profile
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        genre = self.get_argument('genre', first_element(settings['movie']['filters']['genres']))
        if genre not in settings['movie']['filters']['genres']:
            genre = first_element(settings['movie']['filters']['genres'])

        country = self.get_argument('country', first_element(settings['movie']['filters']['countries']))
        if country not in settings['movie']['filters']['countries']:
            country = first_element(settings['movie']['filters']['countries'])

        year = self.get_argument('year', first_element(settings['movie']['filters']['years']))
        if year not in settings['movie']['filters']['years']:
            year = first_element(settings['movie']['filters']['years'])

        sort = self.get_argument('sort', first_element(settings['movie']['presentation']['sort']))
        if sort not in settings['movie']['presentation']['sort']:
            sort = first_element(settings['movie']['presentation']['sort'])

        resource = self.get_argument('resource', first_element(settings['movie']['presentation']['resource']))
        if resource not in settings['movie']['presentation']['resource']:
            resource = first_element(settings['movie']['presentation']['resource'])

        page = self.get_argument('page', 1)
        try:
            page = int(page)
        except:
            page = 1
        if page <= 0:
            page = 1

        query = {}
        if genre == last_element(settings['movie']['filters']['genres']):
            query['genres'] = {'$nin': get_body(settings['movie']['filters']['genres'])}
        elif genre != first_element(settings['movie']['filters']['genres']):
            query['genres'] = genre

        if country == last_element(settings['movie']['filters']['countries']):
            query['countries'] = {'$nin': get_body(settings['movie']['filters']['countries'])}
        elif country != first_element(settings['movie']['filters']['countries']):
            query['countries'] = country

        if year == last_element(settings['movie']['filters']['years']):
            query['year'] = {'$lt': '1980'}
        elif year == '80年代':
            query['year'] = {'$gte': '1980', '$lt': '1990'}
        elif year == '90年代':
            query['year'] = {'$gte': '1990', '$lt': '2000'}
        elif year == '00年代':
            query['year'] = {'$gte': '2000', '$lt': '2009'}
        elif year != first_element(settings['movie']['filters']['years']):
            query['year'] = year

        if resource == '只显示在线观看':
            query['resources.online'] = {'$exists': True}
        elif resource == '只显示下载资源':
            query['resources.offline'] = {'$exists': True}

        sort_by = None
        if sort == '热度':
            sort_by = None
        elif sort == '评分':
            sort_by = [('douban.rating', -1)]
        elif sort == '上映日期':
            sort_by = [('year', -1)]

        try:
            result, error = yield tornado.gen.Task(mongodb['movies'].find,
                                                     query,
                                                     fields={'summary': 0},
                                                     skip=(page - 1) * settings['movie']['page_size'],
                                                     limit=settings['movie']['page_size'],
                                                     sort=sort_by)
        except:
            raise tornado.web.HTTPError(500)

        if error.get('error'):
            raise tornado.web.HTTPError(500)

        # set user behaviors: to_watch, watched and not_interested
        movies = result[0]
        user = self.params.get('user')
        if user and movies:
            try:
                user_id = user.get('_id')
                result, error = yield tornado.gen.Task(mongodb['user_behaviors'].find,
                                                       {'user_id': user_id, 'movie_id': {'$in': [movie.get('_id') for movie in movies]}})
                user_behaviors = result[0]
                for behavior in user_behaviors:
                    for movie in movies:
                        if behavior.get('movie_id') == movie.get('_id'):
                            if behavior.get('behavior_type'):
                                movie['my_behavior'] = behavior.get('behavior_type')
                            if behavior.get('rating'):
                                movie['my_rating'] = behavior.get('rating')
            except:
                raise tornado.web.HTTPError(500)

            if error.get('error'):
                raise tornado.web.HTTPError(500)

        response = {
            'movies': movies,
            'more': True if len(movies) >= settings['movie']['page_size'] else False
        }

        self.write(json.dumps(response, cls=JSONEncoderExt))
        self.finish()
