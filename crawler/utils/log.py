'''
Created on Dec 3, 2012

@author: Fang Jiaguo
'''
import logging.handlers
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
LOG_FILE_PATH = os.path.join(os.path.join(PROJECT_ROOT, 'logs'), 'crawler.log')

class Log():
    '''
    Log class
    '''

    def __init__(self):
        handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE_PATH, 'midnight', 1, 30)
        formatter = logging.Formatter("[%(asctime)s] %(message)s")
        handler.setFormatter(formatter)
        # Note: if we use logger.addHandler(handler), we must first call
        # logger.removeHandler(handler). Otherwise there will be many handlers.
        logger = logging.getLogger()
        logger.handlers = [handler]
        logger.setLevel(logging.NOTSET)

        self.__log = logger

    def error(self, msg):
        self.__log.error('[ERROR] %s', msg)

    def info(self, msg):
        self.__log.info('[INFO] %s', msg)

    def debug(self, msg):
        self.__log.debug('[DEBUG] %s', msg)

    def warning(self, msg):
        self.__log.warning('[WARNING] %s', msg)

    def exception(self, msg):
        self.__log.exception('[EXCEPTION] %s', msg)

log = Log()
