"""forum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from investors.views import InvestorViewSet
from projects.views import ProjectViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from startups.views import StartupViewSet

router = DefaultRouter()

router.register(r"startups", StartupViewSet, basename="startups")
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"investors", InvestorViewSet, basename="investors")
# router.register(r'messages', MessageViewSet, basename='messages') #TODO: Implement the MessageViewSet logic


urlpatterns = [
    path("", include("startups.urls")),  # Main page
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/users/", include("users.urls")),
    path("api/notifications/", include("notifications.urls"))
]
