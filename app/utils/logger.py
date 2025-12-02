# app/utils/logger.py
import logging, os
from logging import Logger

def get_logger(name: str = __name__) -> Logger:
    lvl = os.getenv('LOG_LEVEL', 'INFO').upper()
    logger = logging.getLogger(name)
    if not logger.handlers:
        ch = logging.StreamHandler()
        fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    logger.setLevel(getattr(logging, lvl, logging.INFO))
    return logger
