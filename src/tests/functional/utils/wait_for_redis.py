import time
import sys
import redis
import logging

from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from tests.functional.logger import logger


HOST = 'redis'

r = redis.Redis(host=HOST)
while True:
    if r.ping():
        logger.info('Redis ping Ok')
        break
    time.sleep(1)
