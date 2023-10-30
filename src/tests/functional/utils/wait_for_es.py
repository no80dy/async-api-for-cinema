import time

from elasticsearch import Elasticsearch

HOST = 'elastic'


es_client = Elasticsearch(hosts=f'{HOST}:9200')
while True:
    if es_client.ping():
        print('Elasticsearch ping Ok')
        break
    time.sleep(1)
