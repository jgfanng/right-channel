'''
Created on May 25, 2013

@author: yapianyu
'''
from bson.objectid import ObjectId
from difflib import SequenceMatcher
from pyes.es import ES
from pyes.query import MultiMatchQuery, Search
from pymongo.connection import Connection
import collections
import datetime

ml_100k_folder = '/home/yapianyu/Desktop/movielens/ml-100k/'
ml_10m_folder = '/home/yapianyu/Desktop/movielens/ml-10M100K/'
mongodb = Connection('127.0.0.1', 27017)['right-channel']
elasticsearch = ES(('http', '127.0.0.1', 9200))

def count_movie_num_each_year():
    movie_num = {}
    f = open(ml_10m_folder + 'movies.dat')
    for line in f:
        year = int(line.split('::')[1][-5:-1])
        if year in movie_num:
            movie_num[year] += 1
        else:
            movie_num[year] = 1

    d = collections.OrderedDict(sorted(movie_num.items(), key=lambda t:-t[0]))
    for year, num in d.items():
        print year, '\t', num

def create_72000_users():
    for uid in range(1, 72001):
        name = 'ml' + str(uid)
        email = 'ml' + str(uid) + '@movielens.org'
        mongodb['accounts'].insert({'nick_name': name, 'email': email, 'password': '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'})
        print uid

def calc_similarity(s_standard, s_candidate):
    if s_standard is None or s_candidate is None:
        return 0

    m = SequenceMatcher(None, s_standard, s_candidate)
    if len(s_standard) >= len(s_candidate):
        return m.ratio()

    # each block represents a sequence of matching characters in a string
    # of the form (idx_1, idx_2, len)
    # the best partial match will block align with at least one of those blocks
    #   e.g. shorter = "abcd", longer = XXXbcdeEEE
    #   block = (1,3,3)
    #   best score === ratio("abcd", "Xbcd")
    blocks = m.get_matching_blocks()
    scores = []
    for block in blocks:
        start = block[1] - block[0] if (block[1] - block[0]) > 0 else 0
        end = start + len(s_standard)
        s_sub = s_candidate[start:end]

        m = SequenceMatcher(None, s_standard, s_sub)
        scores.append(m.ratio())

    return max(scores)

def find_most_similar_movie(movie_title, movie_year):
    query = MultiMatchQuery(['title', 'original_title', 'aka'], movie_title)
    results = elasticsearch.search(Search(query=query, size=50), indices='rightchannel', doc_types='movie')
    max_score = 0
    max_movie = None
    for r in results:
        title = r.get('title')
        original_title = r.get('original_title')
        aka = r.get('aka')
        year = r.get('year')
        
        if year and year == movie_year:
            score = 0
            if title:
                score = max(calc_similarity(title, movie_title), score)
            if original_title:
                score = max(calc_similarity(original_title, movie_title), score)
            if aka:
                for t in aka:
                    score = max(calc_similarity(t, movie_title), score)
    
            if score > max_score:
                max_score = score
                max_movie = r
    
            if max_score > 0.9999:
                break

    return max_movie, max_score

def import_ml_100k_to_mongodb():
    # create email dict
    email2objid = {}
    for r in mongodb['accounts'].find():
        email2objid[r['email']] = r['_id']

    # create mid dict
    mid2title = {}
    mid2year = {}
    f = open(ml_100k_folder + 'u.item')
    for line in f:
        try:
            fields = line.split('|')
            mid = fields[0]
            title = fields[1]
            year = title[-5:-1]
            title = title[:title.index('(')].decode('utf-8')
            mid2title[mid] = title
            mid2year[mid] = year
        except:
            pass

    f = open(ml_100k_folder + 'u.data')
    for line in f:
        try:
            uid, mid, rating, _ = tuple(line.split())
            email = 'ml' + str(uid) + '@movielens.org'
            title = mid2title[mid]
            year = mid2year[mid]
            rating = float(rating)

            similar_movie, score = find_most_similar_movie(title, year)
            if similar_movie:
                mongodb['ml_100k_ratings'].update({'user_id': email2objid[email], 'movie_id': ObjectId(similar_movie['_id'])},
                                                  {'$set': {'rating': rating, 'last_updated': datetime.datetime.utcnow()}},
                                                  upsert=True)
        except:
            pass
        print score, uid, mid, rating

def import_ml_10m_to_mongodb():
    # create email dict
    email2objid = {}
    for r in mongodb['accounts'].find():
        email2objid[r['email']] = r['_id']

    # create mid dict
    mid2title = {}
    mid2year = {}
    f = open(ml_10m_folder + 'movies.dat')
    for line in f:
        mid, title, _ = tuple(line.split('::'))
        year = title[-5:-1]
        title = title[:title.index('(')].decode('utf-8')
        mid2title[mid] = title
        mid2year[mid] = year

    f = open(ml_10m_folder + 'ratings.dat')
    for line in f:
        uid, mid, rating, _ = tuple(line.split('::'))
        email = 'ml' + str(uid) + '@movielens.org'
        title = mid2title[mid]
        year = mid2year[mid]
        rating = float(rating)

        if int(year) < 1990:  # need to ignore those early than 1990
            print year, line.strip()
            continue

        similar_movie, score = find_most_similar_movie(title, year)
        if similar_movie:
            mongodb['ratings'].update({'user_id': email2objid[email], 'movie_id': ObjectId(similar_movie['_id'])},
                                      {'$set': {'rating': rating, 'last_updated': datetime.datetime.utcnow()}},
                                      upsert=True)
            print score, uid, mid, rating

import_ml_10m_to_mongodb()