import os

from django.core.mail import send_mail


class Util:
    @staticmethod
    def send_email(data):
        send_mail(subject=data['email_subject'], message=data['email_body'],
                  from_email=os.environ.get('EMAIL_HOST_USER'), recipient_list=[data['to_email']])
