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
from django.urls import path, include
from projects.views import ProjectViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.routers import DefaultRouter
from startups.views import StartupViewSet
from users.views import PasswordResetRequest, PasswordResetConfirm
from investors.views import InvestorViewSet

router = DefaultRouter()

router.register(r'startups', StartupViewSet, basename='startups')
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'investors', InvestorViewSet, basename='investors')
# router.register(r'messages', MessageViewSet, basename='messages') #TODO: Implement the MessageViewSet logic


urlpatterns = [
    path('', include('startups.urls')),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('users/', include('users.urls')),
    path('startups/', include('startups.urls')),
    path('reset_password/', PasswordResetRequest.as_view(), name='reset_password'),
    path('reset_password/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('api/users/', include('users.urls')),
]
