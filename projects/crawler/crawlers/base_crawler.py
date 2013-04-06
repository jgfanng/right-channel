# -*- coding: utf-8 -*-

'''
Created on Nov 29, 2012

@author: Fang Jiaguo
'''
from settings import elasticsearch, settings

class BaseCrawler(object):
    def find_most_similar_movie(self, title, year, countries, directors, casts):
        self._find_most_similar('movie', title, year, countries, directors, casts)

    def find_most_similar_tv(self, title, year, countries, directors, casts):
        self._find_most_similar('tv', title, year, countries, directors, casts)

    def _find_most_similar(self, doc_type, title, year, countries, directors, casts):
        if title:
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
            result = elasticsearch.search(query, index=settings['elasticsearch']['index'], doc_type=doc_type, size=10)
            max_score = 0
            for r in result.get('hits').get('hits'):
                title_ = r.get('_source').get('title')
                original_title_ = r.get('_source').get('original_title')
                aka_ = r.get('_source').get('aka')
                year_ = r.get('_source').get('year')
                countries_ = r.get('_source').get('countries')
                directors_ = r.get('_source').get('directors')
                casts_ = r.get('_source').get('casts')

                score = 0
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
                    for cast in casts_:
                        if cast in casts_:
                            score += 1
                max_score = max(max_score, score)

            return max_score

        return None
