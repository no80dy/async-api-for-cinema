import time

from elasticsearch import Elasticsearch

HOST = 'localhost'

es_client = Elasticsearch(hosts=f'http://{HOST}:9200', validate_cert=False, use_ssl=False)
while True:
    if es_client.ping():
        break
    time.sleep(1)