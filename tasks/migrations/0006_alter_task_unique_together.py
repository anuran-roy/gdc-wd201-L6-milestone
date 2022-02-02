# Generated by Django 4.0.1 on 2022-01-31 22:05

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0005_alter_task_priority'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='task',
            unique_together={('user', 'priority')},
        ),
    ]