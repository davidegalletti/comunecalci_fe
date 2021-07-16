# Generated by Django 3.2.3 on 2021-07-08 19:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('segnala', '0016_auto_20210531_0921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='attiva',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='Notifica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('journal_id', models.IntegerField(db_index=True)),
                ('email_tentativo', models.IntegerField(default=0)),
                ('stato', models.CharField(choices=[('INIZIALE', 'INIZIALE'), ('EMAIL_FALLITO', 'EMAIL_FALLITO'), ('EMAIL_INVIATO', 'EMAIL_INVIATO')], default='INIZIALE', max_length=50)),
                ('testo_da_inviare', models.TextField()),
                ('segnalazione', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='segnala.segnalazione')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
