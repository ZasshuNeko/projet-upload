# Generated by Django 3.0.7 on 2020-10-15 07:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0016_log_info'),
    ]

    operations = [
        migrations.RenameField(
            model_name='log',
            old_name='etude',
            new_name='action',
        ),
    ]