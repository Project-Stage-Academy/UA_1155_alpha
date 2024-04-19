# Generated by Django 5.0.4 on 2024-04-19 11:10

import django.db.models.functions.datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_registration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='registration_date',
            field=models.DateTimeField(db_default=django.db.models.functions.datetime.Now()),
        ),
    ]
