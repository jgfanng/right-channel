'''
Created on Dec 3, 2012

@author: Fang Jiaguo
'''
import logging.handlers
import os

def get_logger(name, log_file):
    # Severity level: DEBUG/INFO/WARN/ERROR/CRITICAL
    logger = logging.getLogger(name)
    # Set to DEBUG when the application is under debugging, otherwise INFO.
    logger.setLevel(logging.DEBUG)
    # Create file handler with INFO log level accepting higher severity level than INFO.
    file_handler = logging.handlers.RotatingFileHandler(os.path.join('logs', log_file), maxBytes=1024 * 1024 * 1024 * 2, backupCount=3)
    file_handler.setLevel(logging.DEBUG)
    # Create console handler with a higher DEBUG level accepting higher severity level than DEBUG.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # Create formatter and add it to the handlers
    formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    # Add handlers to logger.
    logger.handlers = [file_handler, console_handler]

    return logger
