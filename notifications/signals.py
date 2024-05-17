from django.db.models.signals import post_save
from django.dispatch import receiver

from investors.models import Investor
from projects.models import Project
from startups.models import Startup
from .tasks import send_for_moderation


@receiver(post_save, sender=Startup)
@receiver(post_save, sender=Project)
@receiver(post_save, sender=Investor)
def profile_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal handler to perform actions when a startup is created or updated.
    """
    app_label = sender._meta.app_label
    data_type = sender.__name__
    data_id = instance.id
    send_for_moderation.delay(app_label, data_type, data_id)
