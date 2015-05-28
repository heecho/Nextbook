import os
import django

import redis
from rq import Worker, Queue, Connection
django.setup()
DJANGO_SETTINGS_MODULE = "nextbook.settings"

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()