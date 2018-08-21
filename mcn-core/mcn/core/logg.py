import os
import sys
import logging


LOG_FORMAT = (
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:] %(message)s"
)


def get_logger(name):
    logger = logging.getLogger(name)
    add_log_stream_handler(logger)
    return logger


def add_log_stream_handler(logger):
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
        logger.setLevel(
            logging.DEBUG if int(os.environ.get("DEBUG", 0)) else logging.INFO
        )
