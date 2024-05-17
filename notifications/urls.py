from django.urls import path
from .views import approve, decline

urlpatterns = [
    path("approve/<str:model_name>/<int:data_id>", approve, name='approve'),
    path("decline/<str:model_name>/<int:data_id>", decline, name='decline'),
]


