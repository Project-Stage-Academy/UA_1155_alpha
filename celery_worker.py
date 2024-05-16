import os

from celery import Celery

app = Celery('forum', broker=os.environ.get("REDIS_URL"))

if __name__ == '__main__':
    app.start()
