from datetime import datetime

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.functions import Now


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.registration_date = datetime.now()
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password = models.CharField(max_length=128)
    is_email_valid = models.BooleanField(default=False)
    profile_img_url = models.CharField(max_length=1000, blank=True, default="")
    is_active_for_proposals = models.BooleanField(default=False)
    is_investor = models.BooleanField(default=False)
    is_startup = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    registration_date = models.DateTimeField(db_default=Now())
    last_login = models.DateTimeField(db_default=Now())

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"ID: {self.id}, Email: {self.email}"

    @staticmethod
    def create_user(
        email,
        first_name,
        password,
        last_name,
        profile_img_url="",
        is_active_for_proposals=False,
    ):
        """
        Create a user with the given email, first name, password, last_name , profile image URL,
        is_active_for_proposals, is_investor, and is_startup.
        This method checks that the email, first name, and surname, are not longer than 50 characters,
        and that the password is not longer than 128 characters.

        The validation for email and password realized in UserRegisterSerializer.
        """
        if (
            len(email) <= 50
            and len(first_name) <= 50
            and len(last_name) <= 50
            and len(password) <= 128
        ):
            custom_user = CustomUser(
                email=email,
                first_name=first_name,
                last_name=last_name,
                profile_img_url=profile_img_url,
                is_active_for_proposals=is_active_for_proposals,
            )
            custom_user.set_password(password)
            custom_user.save()
            return custom_user
