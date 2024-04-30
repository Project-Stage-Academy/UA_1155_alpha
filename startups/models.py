from django.db import models
from django.db.models.functions import Now


class Startup(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey('users.CustomUser', related_name='owner', on_delete=models.CASCADE)
    startup_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    industries = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=128, blank=True)
    contact_email = models.CharField(max_length=128, unique=True)
    number_for_startup_validation = models.IntegerField(null=True)
    is_verified = models.BooleanField(default=False)
    registration_date = models.DateTimeField(db_default=Now())

    class Meta:

        db_table = 'startups'


class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    INDUSTRY_CHOICES = [
        ('tech', 'Technology'),
        ('finance', 'Finance'),
        ('healthcare', 'Health Care'),
        ('education', 'Education'),
        ('economics', 'Economics')
    ]

    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='projects')
    project_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    goals = models.CharField(max_length=255)
    budget_needed = models.DecimalField(max_digits=10, decimal_places=2)
    budget_ready = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    industry = models.CharField(max_length=255, choices=INDUSTRY_CHOICES)
    promo_photo_url = models.CharField(max_length=1000, blank=True)
    promo_video_url = models.CharField(max_length=1000, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    registration_date = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    subscribers = models.ManyToManyField('investors.Investor', related_name='subscribed_projects', blank=True)
    investors = models.ManyToManyField('investors.Investor', related_name='participated_projects', blank=True)

    class Meta:
        db_table = 'projects'