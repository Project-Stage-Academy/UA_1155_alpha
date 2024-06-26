"""library URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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

from django.urls import path

from .views import (
    LoginAPIView,
    LogoutAPIView,
    PasswordResetConfirm,
    PasswordResetRequest,
    SendEmailConfirmationAPIView,
    UserRegisterAPIView,
    UserProfileView,
)

urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path(
        "verify-email/<str:token>/",
        SendEmailConfirmationAPIView.as_view(),
        name="verify-email",
    ),
    path("reset_password/", PasswordResetRequest.as_view(), name="reset_password"),
    path(
        "reset_password/<token>/",
        PasswordResetConfirm.as_view(),
        name="password_reset_confirm",
    ),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]
