import os

from django.apps import apps
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


def get_serializer(model_name, instance):
    """
    Get the serializer based on the model_name.
    """
    if model_name == "Investor":
        return InvestorSerializer(instance)
    elif model_name == "Project":
        return ProjectSerializer(instance)
    elif model_name == "Startup":
        return StartupSerializer(instance)
    else:
        raise ValueError("Invalid data_type")


def get_model_by_name(model_name):
    """
    Get the model based on the model_name.
    """
    for model in apps.get_models():
        if model.__name__ == model_name:
            return model
    raise LookupError(f"Model '{model_name}' not found.")
