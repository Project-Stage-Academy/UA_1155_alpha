# Generated by Django 5.0.4 on 2024-04-19 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_rename_user_id_customuser_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='investor',
            old_name='investor_id',
            new_name='id',
        ),
    ]