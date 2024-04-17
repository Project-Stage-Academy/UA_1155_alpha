from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.functions import Now


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.registration_date = datetime.now()
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    is_email_valid = models.BooleanField(default=False)
    profile_img_url = models.CharField(max_length=1000, blank=True)
    is_active_for_proposals = models.BooleanField(default=False)
    is_investor = models.BooleanField(default=False)
    is_startup = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    registration_date = models.DateTimeField(db_default=Now())

    objects = CustomUserManager()

    # Указание email в качестве основного поля для аутентификации
    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"ID: {self.user_id}, Email: {self.email}"


class Investor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
    contact_phone = models.CharField(max_length=128)
    contact_email = models.CharField(max_length=128)
    investment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interests = models.CharField(max_length=500)

    class Meta:
        db_table = 'investors'
        verbose_name = 'Investor'
        verbose_name_plural = 'Investors'

    def __str__(self):
        return f"Investor: {self.full_name}. E-mail: {self.contact_email}"