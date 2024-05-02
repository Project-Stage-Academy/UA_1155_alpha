import os
from celery import shared_task
from django.core.mail import send_mail
from .models import Notification


def send_email_util(email_subject, email_body, to_email):
    send_mail(subject=email_subject, message=email_body,
              from_email=os.environ.get('EMAIL_HOST_USER'), recipient_list=[to_email])


@shared_task(bind=True)
def project_updating(self, investor_id, project_id):
    # Notification(investor_id=investor_id, project_id=project.id, )
    pass
