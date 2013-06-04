'''
Created on Jun 3, 2013

@author: yapianyu
'''
from difflib import SequenceMatcher
from pyes.es import ES
from pyes.query import MultiMatchQuery, Search
from pymongo.connection import Connection
import codecs

ml_10m_folder = '/home/yapianyu/Desktop/movielens/ml-10M100K/'
mongodb = Connection('127.0.0.1', 27017)['right-channel']
elasticsearch = ES(('http', '127.0.0.1', 9200))

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

    return max_movie

def refine_movielens_movie_info():
    # create mid dict
    fin = codecs.open(ml_10m_folder + 'movies.dat', encoding='utf-8')
    fout = codecs.open(ml_10m_folder + 'movies2.dat', mode='w', encoding='utf-8')
    for line in fin:
        line = line.strip()
        fields = line.split('::')
        title = fields[1]
        year = title[-5:-1]
        title = title[:title.index('(')]

        similar_movie = find_most_similar_movie(title, year)
        if similar_movie:
            line = '::'.join([line, str(similar_movie.get('title')), str(similar_movie.get('douban').get('rating'))])
        else:
            line = '::'.join([line, str(None), str(None)])
        print line
        line = line + '\n'
        fout.write(line)

refine_movielens_movie_info()
