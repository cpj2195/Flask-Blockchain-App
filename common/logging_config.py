'''
set and configure a common module logger
'''
import logging
import logging.handlers
import os
from common import configuration

log_folder = configuration.system['log_folder']
if not os.path.exists(log_folder): os.mkdir(log_folder)
applogger = logging.getLogger(configuration.system['app_name'])
#do not propogate logs to the root logger
applogger.propagate = False
logging_level = logging.DEBUG


def configure_app_logger(debug=False):
    '''configure common module logger'''
    global applogger
    global logging_level
    if debug:
        log_level = logging.DEBUG
        log_formatter = logging.Formatter(\
        fmt='%(asctime)s : %(levelname)-8s %(message)-81s <- %(module)s.%(funcName)s, line %(lineno)d',\
        datefmt='%d/%b/%y %I:%M:%S%p')
    else:
        log_level = logging.INFO
        log_formatter = logging.Formatter(fmt='%(asctime)s : %(levelname)-8s %(message)s',\
                                          datefmt='%d/%b/%y %I:%M:%S%p')
    if configuration.config_name == 'testing_config': log_level = logging.ERROR
    logging_level = log_level
    file_handler = logging.handlers.WatchedFileHandler(
    os.path.join(log_folder, '{a}_{c}.log'.format(a=configuration.system['app_name'], c=configuration.config_name)))
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_formatter)
    applogger.setLevel(log_level)
    applogger.addHandler(file_handler)
    applogger.addHandler(console_handler)
