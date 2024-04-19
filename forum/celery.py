from celery import Celery

app = Celery('forum', broker='redis://redis:6379/0')