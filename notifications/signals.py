from django.contrib.sites.shortcuts import get_current_site

from forum.middleware import get_current_request
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from investors.models import Investor
from projects.models import Project
from startups.models import Startup
from .tasks import send_for_moderation, project_updating, project_subscription
from .utils import Util

project_updated_signal = Signal()
project_subscription_signal = Signal()
project_updated_signal_interests = Signal()


@receiver(post_save, sender=Startup)
@receiver(post_save, sender=Project)
@receiver(post_save, sender=Investor)
def profile_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal handler to perform actions when a startup is created or updated.
    """
    request = get_current_request()
    domain = get_current_site(request).domain if request else "localhost:8000/"
    model_name = sender.__name__
    data_id = instance.id
    send_for_moderation.delay(model_name, data_id, domain)


@receiver(project_updated_signal)
def project_updated_receiver(sender, investor_id, project_id, **kwargs):
    """
    Signal handler to perform actions when a project updated.
    """
    request = get_current_request()
    current_site = get_current_site(request).domain if request else "localhost:8000/"
    project_updating.delay(investor_id, project_id, current_site)


@receiver(project_subscription_signal)
def project_subscription_receiver(sender, project_id, subscriber_id, **kwargs):
    """
    Signal handler to perform actions when an investor subscribes to a project.
    """
    request = get_current_request()
    current_site = get_current_site(request).domain if request else "localhost:8000/"
    project_subscription.delay(project_id, subscriber_id, current_site)


@receiver(project_updated_signal_interests)
def project_updated_receiver_interests(sender, project_id, **kwargs):
    """
    Signal handler to perform actions when a project is updated and investor's interests match project's industry.
    """
    request = get_current_request()
    current_site = get_current_site(request).domain if request else "localhost:8000/"

    project = Project.objects.get(id=project_id)
    interested_investors = Investor.objects.filter(interests__name=project.industry.name)

    for investor in interested_investors:
        project_updating.delay(investor.id, project_id, current_site)


@receiver(post_save, sender=Project)
def project_creation_notification(sender, instance, created, **kwargs):
    """
    Signal handler to perform actions when a new project is created.
    """
    try:
        request = get_current_request()
        domain = get_current_site(request).domain if request else "localhost:8000/"
        interested_investors = Investor.objects.filter(interests__name=instance.industry.name)
        for investor in interested_investors:
            subject = f"New Project Created: {instance.project_name}"
            sent_data = {"email_subject": "Project Created",
                         "email_body": f"Hello {investor.user.first_name}!\n" + f"The new project "
                         f"{instance.project_name} has been created.\n" + f"Link to the project: {domain}",
                         "to_email": investor.contact_email}
            Util.send_email(sent_data)
    except Exception as e:
        print(f"Error in project_creation_notification: {e}")

