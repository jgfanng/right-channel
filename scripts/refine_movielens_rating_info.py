'''
Created on Jun 4, 2013

@author: yapianyu
'''
import codecs

ml_10m_folder = '/home/yapianyu/Desktop/movielens/ml-10M100K/'
def refine_movielens_rating_info():
    # create mid dict
    fin = codecs.open(ml_10m_folder + 'ratings.dat')
    fout = codecs.open(ml_10m_folder + 'ratings2.dat', mode='w')
    for line in fin:
        line = line[:line.rindex('::')].replace('::', ',') + '\n'
        print line
        fout.write(line)

refine_movielens_rating_info()