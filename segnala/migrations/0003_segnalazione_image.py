# Generated by Django 3.2.2 on 2021-05-07 09:22

from django.db import migrations, models
import segnala.models


class Migration(migrations.Migration):

    dependencies = [
        ('segnala', '0002_auto_20210507_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='segnalazione',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='foto/%Y/%m/%d/'),
        ),
    ]
