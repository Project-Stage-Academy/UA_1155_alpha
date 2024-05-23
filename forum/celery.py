import os
from celery import Celery, shared_task
from django.core.mail import send_mail

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum.settings')
app = Celery('forum')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@shared_task
def send_email_notification(subject, message, recipient_list):
    send_mail(subject, message, 'postmaster@sandboxfe2a54ed4bab462789981abc4acfa340.mailgun.org', recipient_list)
