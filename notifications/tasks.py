from celery import shared_task
from django.shortcuts import get_object_or_404

from investors.models import Investor
from investors.serializers import InvestorSerializer
from projects.models import Project
from projects.serializers import ProjectSerializer
from startups.models import Startup
from startups.serializers import StartupSerializer
from users.models import CustomUser
from .models import Notification
from .utils import Util


@shared_task(bind=True)
def project_updating(self, investor_id, project_id, domain):
    """
    Celery task for notifying an investor about updates on a project.

    Args:
        self: The task instance.
        investor_id (int): The ID of the investor to notify.
        project_id (int): The ID of the project being updated.
        domain (str): The domain name used to construct links in the notification email.

    Returns:
        str: A message indicating the completion of the task.
    """
    project = Project.objects.get(id=project_id)
    investor = Investor.objects.get(id=investor_id)
    user = CustomUser.objects.get(id=investor.user_id)
    notification = Notification.create_notification(
        recipient_type="investor",
        recipient_id=user.id,
        project_id=project_id,
        type_of_notification="project_updating",
        text=f"Project {project.project_name} has been updated",
    )

    link = f"http://{domain}/api/projects/{project.id}"
    sent_data = {
        "email_subject": "Project Updated",
        "email_body": f"Hello {user.first_name}!\n" +
                      f"The project {project.project_name} has been updated.\n" +
                      f"Link to the project: {link}",
        "to_email": investor.contact_email
    }
    Util.send_email(sent_data)
    return "Project updating task completed"


@shared_task(bind=True)
def project_subscription(self, project_id, subscriber_id, domain):
    """
    Celery task for notifying a startup owner about a new subscription by an investor.

    Args:
        self: The task instance.
        project_id (int): The ID of the project being subscribed to.
        subscriber_id (int): The ID of the investor subscribing to the project.
        domain (str): The domain name used to construct links in the notification email.

    Returns:
        str: A message indicating the completion of the task.
    """
    subscriber = Investor.objects.get(id=subscriber_id)
    subscriber_user = CustomUser.objects.get(id=subscriber.user_id)
    project = Project.objects.get(id=project_id)
    startup = Startup.objects.get(id=project.startup_id)
    recipient_user = startup.owner
    notification = Notification.create_notification(
        recipient_type="startup",
        recipient_id=recipient_user.id,
        project_id=project_id,
        type_of_notification="investor_subscription",
        text=f"Investor {subscriber_user.first_name} {subscriber_user.last_name} subscribed to " +
             f"Project with id {project_id}"
    )
    link = f"http://{domain}/api/projects/{project.id}"
    sent_data = {
        "email_subject": "New project subscription",
        "email_body": f"Hello {recipient_user.first_name}!\n" +
                      f"Investor {subscriber_user.first_name} {subscriber_user.last_name} subscribed " +
                      f"to your project {project.project_name} with id # {project_id}\n" +
                      f"Link to the project: {link}",
        "to_email": startup.contact_email
    }
    Util.send_email(sent_data)
    return "Project subscription task completed"


# WILL BE REMOVED!!!
TRUSTED_ADMIN_EMAIL = "olegtsirkun@gmail.com"


def get_serializer(data_type, instance):
    """
    Get the serializer based on the data_type.
    """
    if data_type.__name__ == "Investor":
        return InvestorSerializer(instance)
    elif data_type.__name__ == "Project":
        return ProjectSerializer(instance)
    elif data_type.__name__ == "Startup":
        return StartupSerializer(instance)
    else:
        raise ValueError("Invalid data_type")


@shared_task(bind=True)
def send_for_moderation(self, data_type, data_id):
    """
    Celery task to send email notification to the admin when any profile is updated.
    """
    instance = get_object_or_404(data_type, id=data_id)
    # instance = data_type.objects.get(id=data_id)

    serializer = get_serializer(data_type, instance)
    serializer_data = serializer.data

    subject = f'{data_type.__name__} verification'
    email_body = f'Hello! {data_type.__name__} profile is awaiting moderation\n\n'
    for field, value in serializer_data.items():
        email_body += f'{field}: {value}\n'

    sent_data = {
        "email_subject": subject,
        "email_body": email_body,
        "to_email": TRUSTED_ADMIN_EMAIL,
    }
    Util.send_email(sent_data)
    return "Notification for admin task completed"
