# Generated by Django 3.0.7 on 2020-10-06 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0012_suividocument_background'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jonctionetapesuivi',
            name='etat',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='upload.RefEtatEtape'),
        ),
    ]
