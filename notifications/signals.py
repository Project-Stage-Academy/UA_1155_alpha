from investors.models import Investor
from startups.models import Startup
from projects.models import Project
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_for_moderation


@receiver(post_save, sender=Startup)
@receiver(post_save, sender=Project)
@receiver(post_save, sender=Investor)
def startup_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal handler to perform actions when a startup is created or updated.
    """
    data_type = sender
    data_id = instance.id
    send_for_moderation(data_type, data_id)
