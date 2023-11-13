import time

import backoff
import requests

from elasticsearch import Elasticsearch


HOST = 'elastic'
PORT = 9200
BACKOFF_MAX_TIME = 60


if __name__ == '__main__':
    es_client = Elasticsearch(hosts=f'{HOST}:{PORT}')

    @backoff.on_exception(backoff.expo, (requests.exceptions.Timeout,
                                         requests.exceptions.ConnectionError), max_time=BACKOFF_MAX_TIME)
    def check_es_readiness():
        while True:
            if es_client.ping():
                print('Elasticsearch ping Ok')
                break
            time.sleep(1)

    try:
        check_es_readiness()
    except ConnectionError:
        print('Elasticsearch is not available')
        raise ConnectionError
