from celery import Celery

app = Celery('forum', broker='redis://redis:6379/0')

if __name__ == '__main__':
    app.start()