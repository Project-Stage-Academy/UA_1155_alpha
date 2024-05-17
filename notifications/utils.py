import os

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

from investors.serializers import InvestorSerializer
from projects.serializers import ProjectSerializer
from startups.serializers import StartupSerializer


class Util:
    @staticmethod
    def send_email(data):
        send_mail(subject=data['email_subject'], message=data['email_body'],
                  from_email=os.environ.get('EMAIL_HOST_USER'), recipient_list=[data['to_email']])

    @staticmethod
    def send_html(data):
        html_content = render_to_string(data['html_template'], data['context'])

        email = EmailMultiAlternatives(subject=data['email_subject'], body=data['email_body'],
                                       from_email=os.environ.get('EMAIL_HOST_USER'), to=[data['to_email']])

        email.attach_alternative(html_content, "text/html")
        email.send()


def get_serializer(data_type, instance):
    """
    Get the serializer based on the data_type.
    """
    if data_type == "Investor":
        return InvestorSerializer(instance)
    elif data_type == "Project":
        return ProjectSerializer(instance)
    elif data_type == "Startup":
        return StartupSerializer(instance)
    else:
        raise ValueError("Invalid data_type")
