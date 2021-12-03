import logging
from logging.handlers import RotatingFileHandler
import os

from pythonjsonlogger import jsonlogger


def pull_logger(name, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers = []

    formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(message)s")

    handler = RotatingFileHandler(os.path.join("logs", "app.log"), maxBytes=100000, backupCount=5)
    handler.setLevel(level)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
