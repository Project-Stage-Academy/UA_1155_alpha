from django.urls import path
from .views import approve, decline

urlpatterns = [
    path("approve/", approve, name='approve'),
    path("decline/", decline, name='decline'),
]


