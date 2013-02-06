'''
Created on Feb 6, 2013

@author: Fang Jiaguo
'''
import hashlib

def encrypt(original):
    return hashlib.sha256(original).hexdigest()
