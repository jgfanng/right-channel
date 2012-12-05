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

    def __init__(self, name=None):
        self.__name = name
        # Severity level: DEBUG/INFO/WARN/ERROR/CRITICAL
        self.__logger = logging.getLogger(name)
        # Set to DEBUG when the application is under debugging, otherwise INFO.
        self.__logger.setLevel(logging.DEBUG)
        # Create file handler with INFO log level accepting higher severity level than INFO.
        file_handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE_PATH, 'midnight', 1, 7)
        file_handler.setLevel(logging.INFO)
        # Create console handler with a higher DEBUG level accepting higher severity level than DEBUG.
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        # Create formatter and add it to the handlers
        formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        # Add the handlers to logger.
        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(console_handler)

    def get_child_logger(self, name):
        # Create (but not configure) a child logger, and all logger calls to the child will pass up to the parent.
        return logging.getLogger('.'.join([self.__name, name]))

log = Log('VideoCabin')
