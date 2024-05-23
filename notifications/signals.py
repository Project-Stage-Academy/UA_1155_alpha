from django.contrib.sites.shortcuts import get_current_site
from forum.middleware import get_current_request
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from investors.models import Investor
from projects.models import Project
from startups.models import Startup
from .models import Notification
from .tasks import send_for_moderation, project_updating, project_subscription
from forum.celery import send_email_notification

project_updated_signal = Signal()
project_subscription_signal = Signal()


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


def match_project_to_investor(project, investor):
    project_industries = set(project.industries.values_list('id', flat=True))
    investor_interests = set(investor.interests.values_list('id', flat=True))
    return bool(project_industries & investor_interests)


def send_notification(investor, project, is_new):
    subject = "New Project" if is_new else "Project Update"
    message = f"The project '{project.name}' in your area of interest has been {'created' if is_new else 'updated'}."
    notification = Notification.objects.create(recipient=investor.user, message=message)
    send_email_notification.delay(subject, message, [investor.contact_email])


def notify_investors_about_project(project, is_new):
    investors = Investor.objects.filter(is_active=True, is_verified=True)
    for investor in investors:
        if match_project_to_investor(project, investor):
            send_notification(investor, project, is_new)
