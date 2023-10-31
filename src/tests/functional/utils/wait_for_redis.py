import time

import redis


HOST = 'redis'

r = redis.Redis(host=HOST)
while True:
    if r.ping():

        print('Redis ping Ok')
        break
    time.sleep(1)
