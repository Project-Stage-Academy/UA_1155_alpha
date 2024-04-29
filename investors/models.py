from django.db import models

from startups.models import Project
from users.models import CustomUser



class Investor(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='investors')
    location = models.CharField(max_length=128, blank=True)
    contact_phone = models.CharField(max_length=25, blank=True)
    contact_email = models.EmailField(unique=True, max_length=50)
    investment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interests = models.CharField(max_length=500, blank=True, choices=Project.INDUSTRY_CHOICES)
    number_for_investor_validation = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'investors'
        verbose_name = 'Investor'
        verbose_name_plural = 'Investors'

    def __str__(self):
        return f"Investor: {self.user.first_name}. E-mail: {self.contact_email}"
