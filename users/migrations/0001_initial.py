# Generated by Django 5.0.4 on 2024-04-18 12:14

import django.db.models.deletion
import django.db.models.functions.datetime
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(max_length=128, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('is_email_valid', models.BooleanField(default=False)),
                ('profile_img_url', models.CharField(blank=True, max_length=1000)),
                ('is_active_for_proposals', models.BooleanField(default=False)),
                ('is_investor', models.BooleanField(default=False)),
                ('is_startup', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('registration_date', models.DateTimeField(db_default=django.db.models.functions.datetime.Now())),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='Investor',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('full_name', models.CharField(max_length=128)),
                ('location', models.CharField(max_length=128)),
                ('contact_phone', models.CharField(max_length=128)),
                ('contact_email', models.CharField(max_length=128)),
                ('investment_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('interests', models.CharField(max_length=500)),
            ],
            options={
                'verbose_name': 'Investor',
                'verbose_name_plural': 'Investors',
                'db_table': 'investors',
            },
        ),
    ]
