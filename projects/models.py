from django.db import models
from django.db.models.functions import Now
from startups.models import Startup, Industry


class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='projects')
    project_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    goals = models.CharField(max_length=255)
    budget_needed = models.DecimalField(max_digits=10, decimal_places=2)
    budget_ready = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)
    promo_photo_url = models.CharField(max_length=1000, blank=True)
    promo_video_url = models.CharField(max_length=1000, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    registration_date = models.DateTimeField(default=Now())
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    subscribers = models.ManyToManyField("investors.Investor", related_name='subscribed_projects', blank=True)
    investors = models.ManyToManyField("investors.Investor", related_name='participated_projects', blank=True)
    is_active = models.BooleanField(default=True)
    # is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'projects'
        app_label = 'projects'
