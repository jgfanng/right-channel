'''
Created on May 28, 2013

@author: yapianyu
'''
from pymongo.connection import Connection

data1 = """1,1,5.0
1,2,3.0
1,3,2.5
2,1,2.0
2,2,2.5
2,3,5.0
2,4,2.0
3,1,2.5
3,4,4.0
3,5,4.5
3,7,5.0
4,1,5.0
4,3,3.0
4,4,4.5
4,6,4.0
5,1,4.0
5,2,3.0
5,3,2.0
5,4,4.0
5,5,3.5
5,6,4.0
"""

data2 = """|       1 |     101 |          5 |
|       1 |     102 |          3 |
|       1 |     103 |          2 |
|       2 |     101 |          2 |
|       2 |     102 |        2.5 |
|       2 |     103 |          5 |
|       2 |     104 |          2 |
|       3 |     101 |        2.5 |
|       3 |     104 |          4 |
|       3 |     105 |        4.5 |
|       3 |     107 |          5 |
|       4 |     101 |          5 |
|       4 |     103 |          3 |
|       4 |     104 |        4.5 |
|       4 |     106 |          4 |
|       5 |     101 |          4 |
|       5 |     102 |          3 |
|       5 |     103 |          2 |
|       5 |     104 |          4 |
|       5 |     105 |        3.5 |
|       5 |     106 |          0 |
"""

db = Connection('127.0.0.1', 27017)['right-channel']
for line in data2.splitlines():
    fields = [field.strip() for field in line.split('|') if field.strip()]
    u = fields[0]
    m = fields[1]
    r = float(fields[2])
    db['demo_ratings'].insert({'user_id': u, 'movie_id': m, 'rating': r})
