'''
Created on Dec 25, 2012

@author: Fang Jiaguo
'''
from crawlers.utils.mongodb import movie_douban_collection, \
    movie_douban_correction_collection, movie_store_collection
import datetime

def populate_from_douban_to_store():
    for movie_info in movie_douban_collection.find():
        # REFINE 1: do the correction
        result = movie_douban_correction_collection.find_one({'_id': movie_info['_id']}, fields={'_id': 0})
        if result:
            for key in result.keys():
                movie_info[key] = result[key]
        # REFINE 2: make it more friendly
        movie_info = refine_movie_info(movie_info)
        movie_store_collection.update({'id': movie_info['id']}, {'$set': movie_info}, upsert=True)

def refine_movie_info(movie_info):
    '''
    Refine movie info.
    '''

    new_movie_info = {'id': movie_info['id']}
    if 'attrs' in movie_info and 'year' in movie_info['attrs'] and movie_info['attrs']['year'] and movie_info['attrs']['year'][0]:
        new_movie_info['year'] = movie_info['attrs']['year'][0].strip()  # Caution: may not be provided
    if 'title' in movie_info and movie_info['title']:
        new_movie_info['title'] = movie_info['title'].strip()
    if 'alt_title' in movie_info and movie_info['alt_title']:
        new_movie_info['alt_titles'] = [item.strip() for item in movie_info['alt_title'].split(' / ') if item.strip()]
    if 'attrs' in movie_info and 'director' in movie_info['attrs'] and movie_info['attrs']['director']:
        new_movie_info['directors'] = movie_info['attrs']['director']
    if 'attrs' in movie_info and 'writer' in movie_info['attrs'] and movie_info['attrs']['writer']:
        new_movie_info['writers'] = movie_info['attrs']['writer']
    if 'attrs' in movie_info and 'cast' in movie_info['attrs'] and movie_info['attrs']['cast']:
        new_movie_info['casts'] = movie_info['attrs']['cast']
    if 'attrs' in movie_info and 'episodes' in movie_info['attrs'] and movie_info['attrs']['episodes'] and movie_info['attrs']['episodes'][0]:
        new_movie_info['episodes'] = movie_info['attrs']['episodes'][0]  # Caution: may not be an integer
    if 'attrs' in movie_info and 'movie_type' in movie_info['attrs'] and movie_info['attrs']['movie_type']:
        new_movie_info['types'] = movie_info['attrs']['movie_type']
    if 'attrs' in movie_info and 'country' in movie_info['attrs'] and movie_info['attrs']['country']:
        new_movie_info['countries'] = movie_info['attrs']['country']
    if 'attrs' in movie_info and 'language' in movie_info['attrs'] and movie_info['attrs']['language']:
        new_movie_info['languages'] = movie_info['attrs']['language']
    if 'attrs' in movie_info and 'pubdate' in movie_info['attrs'] and movie_info['attrs']['pubdate']:
        new_movie_info['pubdates'] = movie_info['attrs']['pubdate']
    if 'attrs' in movie_info and 'movie_duration' in movie_info['attrs'] and movie_info['attrs']['movie_duration']:
        new_movie_info['durations'] = movie_info['attrs']['movie_duration']
    if 'image' in movie_info and movie_info['image']:
        new_movie_info['image'] = movie_info['image']
    if 'summary' in movie_info and movie_info['summary']:
        new_movie_info['summary'] = movie_info['summary']

    new_movie_info['douban'] = {'link': 'http://movie.douban.com/subject/%s/' % movie_info['id'], 'last_updated': datetime.datetime.utcnow()}
    if 'rating' in movie_info and 'average' in movie_info['rating'] and movie_info['rating']['average']:
        new_movie_info['douban']['score'] = float(movie_info['rating']['average'])

    return new_movie_info

populate_from_douban_to_store()
