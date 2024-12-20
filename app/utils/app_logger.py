import logging

#Нужно перенастроить логер для более удобоваримого вывода
_log_format = "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"


def stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler

def file_handler(log_file="main.log"):
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler())
    logger.addHandler(file_handler())
    return logger

logging.getLogger('passlib').setLevel(logging.ERROR)