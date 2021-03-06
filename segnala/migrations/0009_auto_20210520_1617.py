# Generated by Django 3.2.3 on 2021-05-20 14:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('segnala', '0008_auto_20210519_1734'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('redmine_id', models.PositiveIntegerField(db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='segnalazione',
            name='token_foto',
            field=models.CharField(blank=True, db_index=True, default='', max_length=100),
        ),
    ]
