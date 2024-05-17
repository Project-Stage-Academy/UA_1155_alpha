from django.urls import path
from .views import approve, decline

urlpatterns = [
    path("approve/<str:model_name>/<int:id>", approve, name='approve'),
    path("decline/<str:model_name>/<int:id>", decline, name='decline'),
]


