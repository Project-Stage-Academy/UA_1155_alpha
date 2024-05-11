from celery import shared_task

from investors.models import Investor
from projects.models import Project
from users.models import CustomUser
from .models import Notification
from .utils import Util


@shared_task(bind=True)
def project_updating(self, investor_id, project_id, domain):
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
