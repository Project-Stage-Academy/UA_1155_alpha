from celery import shared_task

from investors.models import Investor
from projects.models import Project
from users.models import CustomUser
from .models import Notification
from .utils import Util


@shared_task(bind=True)
def project_updating(self, investor_id, project_id):
    project = Project.objects.get(id=project_id)
    investor = Investor.objects.get(id=investor_id)
    user = CustomUser.objects.get(id=investor.user_id)
    notification = Notification(
        investor_id=investor_id,
        project_id=project_id,
        type_of_notification='project_updating',
        text=f"Project {project.project_name} has been updated"
    )
    notification.save()

    sent_data = {
        "email_subject": "Project Updated",
        "email_body": f"Hello {user.first_name}!\nThe project {project.project_name} has been updated.",
        "to_email": investor.contact_email
    }
    Util.send_email(sent_data)
