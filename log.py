import logging
from logging.handlers import RotatingFileHandler

def init_rotating_log(logfile, size, count):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(logfile, maxBytes = size, backupCount = count)

    formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

if __name__ == '__main__':
    import settings
    import config
    settings.init()
    config.readConfigData()
    # initLogFile(config.getLogPath() + config.getMainLogFile())
    init_rotating_log(config.getLogPath() + config.getMainLogFile(), config.getLogFileSize(), config.getLogFileCount())
    # log('debug message', 'DEBUG')
    # log('info message', 'INFO')
    # log('warining message', 'WARNING')
    # log('error message', 'ERROR')
    # log('critical message', 'CRITICAL')
    logger = logging.getLogger(__name__)
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warning message')
    logger.error('error message')
    logger.critical('critical message')