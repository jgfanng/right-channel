# -*- coding: utf-8 -*-

'''
Created on Dec 12, 2012

@author: Fang Jiaguo
'''
import unicodedata

AUXILIARY_WORDS = [u'3d', u' 港', u' 台']

def simplify(title):
    '''
    Simplify a movie title.
    '''

    # 1. to lower case
    title = title.lower()
    # 2. replace punctuation with whitespace
    new_title = ''
    for char in title:
        if ispunctuation(char):
            new_title += ' '
        else:
            new_title += char
    new_title = ' '.join(char for char in new_title.split(' ') if char)
    # 3. remove auxiliary words in the tail if have
    while True:
        end_by_word = False
        for word in AUXILIARY_WORDS:
            if new_title.endswith(word):
                new_title = new_title[:-len(word)].strip()
                end_by_word = True
                break
        if not end_by_word:
            break

    return new_title

def ispunctuation(char):
    '''
    Return true if char is a punctuation, false otherwise.

    General category names are Letter (L), Mark (M), Number (N),
    Punctuation (P), Symbol (S), Separator (Z), and Other (C).
    '''

    return True if unicodedata.category(char).startswith('P') else False
