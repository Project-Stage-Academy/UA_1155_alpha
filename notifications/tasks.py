import os

from celery import shared_task
from django.template.loader import render_to_string
from django.urls import reverse

from investors.models import Investor
from projects.models import Project
from startups.models import Startup
from users.models import CustomUser
from .models import ProjectNotification, Notification
from .utils import Util, get_serializer, get_model_by_name


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
    notification = ProjectNotification.create_notification(recipient_type="investor", recipient_id=user.id,
                                                    project_id=project_id, type_of_notification="project_updating",
                                                    text=f"Project {project.project_name} has been updated", )

    link = f"http://{domain}/api/projects/{project.id}"
    sent_data = {"email_subject": "Project Updated",
                 "email_body": f"Hello {user.first_name}!\n" + f"The project {project.project_name} has been updated.\n" + f"Link to the project: {link}",
                 "to_email": investor.contact_email}
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
    notification = ProjectNotification.create_notification(recipient_type="startup", recipient_id=recipient_user.id,
                                                    project_id=project_id, type_of_notification="investor_subscription",
                                                    text=f"Investor {subscriber_user.first_name} {subscriber_user.last_name} subscribed to " + f"Project with id {project_id}")
    link = f"http://{domain}/api/projects/{project.id}"
    sent_data = {"email_subject": "New project subscription",
                 "email_body": f"Hello {recipient_user.first_name}!\n" + f"Investor {subscriber_user.first_name} {subscriber_user.last_name} subscribed " + f"to your project {project.project_name} with id # {project_id}\n" + f"Link to the project: {link}",
                 "to_email": startup.contact_email}
    Util.send_email(sent_data)
    return "Project subscription task completed"


@shared_task(bind=True)
def send_for_moderation(self, model_name, data_id, domain):
    """
    Celery task to send email notification to the admin when any profile is updated.
    """
    model = get_model_by_name(model_name)

    instance = model.objects.get(id=data_id)

    serializer = get_serializer(model_name, instance)
    serializer_data = serializer.data

    subject = f"{model_name} verification"
    email_body = f"Hello! {model_name} profile is awaiting moderation\n\n"
    for field, value in serializer_data.items():
        email_body += f"{field}: {value}\n"
    to_email = os.environ.get("TRUSTED_ADMIN_EMAIL")

    approve_path = reverse("approve", args=[model_name, data_id])
    decline_path = reverse("decline", args=[model_name, data_id])

    approve_url = f"http://{domain}{approve_path}"
    decline_url = f"http://{domain}{decline_path}"

    sent_data = {"email_subject": subject, "email_body": email_body, "to_email": to_email,
                 "html_template": "content_moderation.html",
                 "context": {"email_body": email_body, "approve_button_link": approve_url,
                             "decline_button_link": decline_url, }}

    Util.send_html(sent_data)

    return "Notification for admin task completed"


@shared_task(bind=True)
def send_approve(self, model_name, contact_email, data_id):
    sent_data = {"email_subject": "Moderation success",
                 "email_body": f"Congratulations, your {model_name} profile passed moderation!",
                 "to_email": contact_email, }

    Notification.create_notification(recipient_type=model_name.lower(), recipient_id=data_id,
                                     text=f"{model_name} profile with id={data_id} passed moderation")

    Util.send_email(sent_data)
    return "Approve notification task completed"


@shared_task(bind=True)
def send_decline(self, model_name, contact_email, data_id):
    sent_data = {"email_subject": "Moderation failed",
                 "email_body": f"Unfortunately, your {model_name} profile did not pass moderation.",
                 "to_email": contact_email, }

    Notification.create_notification(recipient_type=model_name.lower(), recipient_id=data_id,
                                     text=f"{model_name} profile with id={data_id} did not pass moderation")

    Util.send_email(sent_data)
    return "Decline notification task completed"


@shared_task(bind=True)
def project_creation_notification(self, investor_id, project_id, domain):
    """
    Celery task to notify an investor about the creation of a new project.
    """
    try:
        investor = Investor.objects.get(id=investor_id)
        project = Project.objects.get(id=project_id)
        subject = f"New Project Created: {project.project_name}"
        message = (
            f"Hello {investor.user.first_name}!\n"
            f"A new project '{project.project_name}' has been created in the {project.industry.name} industry.\n"
            f"Link to the project: http://{domain}/api/projects/{project_id}/\n"
            f"Best regards,\nYour Project Team"
        )
        Util.send_email({
            'email_subject': subject,
            'email_body': message,
            'to_email': investor.user.email
        })
        return "Project creating task completed"

    except (Investor.DoesNotExist, Project.DoesNotExist) as e:
        print(f"Error: {e}")