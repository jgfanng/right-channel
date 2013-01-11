'''
Created on Jan 9, 2013

@author: Fang Jiaguo
'''
from bson.objectid import ObjectId
from json.encoder import JSONEncoder
import json

class JSONEncoderExt(JSONEncoder):
    def default(self, o):
        if hasattr(o, 'isoformat'):
            return o.isoformat()
        elif isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self.o)
