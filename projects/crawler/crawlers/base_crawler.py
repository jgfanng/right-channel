# -*- coding: utf-8 -*-

'''
Created on Nov 29, 2012

@author: Fang Jiaguo
'''
from settings import elasticsearch, settings
from utilities import calc_similarity
import threading

class BaseCrawler(threading.Thread):
    def find_most_similar_movie(self, title, year, countries, directors, casts):
        return self._find_most_similar_media('movie', title, year, countries, directors, casts)

    def find_most_similar_tv(self, title, year, countries, directors, casts):
        return self._find_most_similar_media('tv', title, year, countries, directors, casts)

    def _find_most_similar_media(self, media, title, year, countries, directors, casts):
        if title is None:
            return None, 0

        query = {
            'query': {
                'multi_match': {
                    'query': title,
                    'fields': [
                        'title',
                        'original_title',
                        'aka'
                    ]
                }
            }
        }
        result = elasticsearch.search(query, index=settings['elasticsearch']['index'], doc_type=media, size=10)
        if result.get('hits').get('total') == 0:
            return None, 0
        max_score = 0; similar_media = None
        for r in result.get('hits').get('hits'):
            title_ = r.get('_source').get('title')
            original_title_ = r.get('_source').get('original_title')
            aka_ = r.get('_source').get('aka')
            year_ = r.get('_source').get('year')
            countries_ = r.get('_source').get('countries')
            directors_ = r.get('_source').get('directors')
            casts_ = r.get('_source').get('casts')

            score = 0
            if title_:
                score = max(calc_similarity(title_, title), score)
            if original_title_:
                score = max(calc_similarity(original_title_, title), score)
            if aka_:
                for t in aka_:
                    score = max(calc_similarity(t, title), score)
            if year and year_ and year == year_:
                score += 1
            if countries and countries_:
                for country in countries:
                    if country in countries_:
                        score += 1
            if directors and directors_:
                for director in directors:
                    if director in directors_:
                        score += 1
            if casts and casts_:
                for cast in casts:
                    if cast in casts_:
                        score += 1

            if score > max_score:
                max_score = score
                similar_media = r

        return similar_media.get('_source').get('title'), max_score
