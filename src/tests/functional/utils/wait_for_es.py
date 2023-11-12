import time
import sys
from pathlib import Path
import logging

from elasticsearch import Elasticsearch

sys.path.append(str(Path(__file__).resolve().parents[3]))

from tests.functional.logger import logger

HOST = 'elastic'


es_client = Elasticsearch(hosts=f'{HOST}:9200')
while True:
    if es_client.ping():
        logger.info('Elasticsearch ping Ok', )
        break
    time.sleep(1)
