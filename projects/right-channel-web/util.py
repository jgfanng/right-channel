'''
Created on Feb 6, 2013

@author: Fang Jiaguo
'''
import hashlib

def encrypt(original):
    return hashlib.sha256(original).hexdigest()

def combine_titles(title, original_title):
    if title and original_title:
        if title != original_title:
            return title + ' / ' + original_title
        else:
            return title
    else:
        return title or original_title
