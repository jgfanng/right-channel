'''
Created on Dec 12, 2012

@author: Fang Jiaguo
'''
import unicodedata

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
    new_title = ' '.join(x for x in new_title.split(' ') if x)
    # 3. remove '3D' in the tail if have
    if new_title != '3d' and new_title.endswith('3d'):
        new_title = new_title[:-2]
    new_title = ' '.join(x for x in new_title.split(' ') if x)

    return new_title

def ispunctuation(char):
    '''
    Return true if char is a punctuation, false otherwise.

    General category names are Letter (L), Mark (M), Number (N),
    Punctuation (P), Symbol (S), Separator (Z), and Other (C).
    '''

    return True if unicodedata.category(char).startswith('P') else False
