'''
Created on Dec 13, 2012

@author: Fang Jiaguo
'''
import time

class LimitedCaller(object):
    '''
    Limit function call under a threshold in a given period.
    Note this functionality is not thread safe.
    '''

    def __init__(self, call, period, maxcall):
        self.__call = call  # the function to call
        self.__period = period  # in seconds
        self.__maxcall = maxcall  # max calls be made in the given period
        self.__times = []

    def __call__(self, *args, **kwargs):
        now = time.time()
        times = [t for t in self.__times if now - t <= self.__period]
        if len(times) >= self.__maxcall:
            t = times[0] + self.__period - now
            time.sleep(t)
        self.__times = times + [time.time()]
        return self.__call(*args, **kwargs)
