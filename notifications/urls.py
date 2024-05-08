from django.urls import path
from .views import NotificationListView, NotificationsAllView

urlpatterns = [
    path('new/', NotificationListView.as_view(), name='new_notifications'),
    path('all/', NotificationsAllView.as_view(), name='all_notifications')
]
