'''
Created on Feb 6, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from json.encoder import JSONEncoder
import hashlib
import json

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

def first_element(l):
    return l[0] if l else None

def last_element(l):
    return l[len(l) - 1] if l else None

def get_body(l):
    return l[1:len(l) - 1] if l and len(l) > 2 else []

class JSONEncoderExt(JSONEncoder):
    def default(self, o):
        if hasattr(o, 'isoformat'):
            return o.isoformat()
        elif isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self.o)
