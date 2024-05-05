from django.db import models
from django.db.models.functions import Now
from users.models import CustomUser

class Industry(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'industries'

class Startup(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(CustomUser, related_name='owner', on_delete=models.CASCADE)
    startup_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    industries = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name='startups', null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=128, unique=True)
    contact_email = models.CharField(max_length=128, unique=True)
    number_for_startup_validation = models.IntegerField(null=True)
    is_verified = models.BooleanField(default=False)
    registration_date = models.DateTimeField(db_default=Now())
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'startups'

