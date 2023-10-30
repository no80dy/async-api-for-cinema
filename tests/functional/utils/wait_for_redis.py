import time

import redis


HOST = 'localhost'

r = redis.Redis(host=HOST, port="6379")
while True:
    if r.ping():
        break
    time.sleep(1)
