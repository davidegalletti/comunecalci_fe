# Generated by Django 4.0.6 on 2023-03-07 10:01

from django.db import migrations, models
import django.db.models.deletion
import mapbox_location_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('segnala', '0018_auto_20220325_1016'),
    ]

    operations = [
        migrations.AddField(
            model_name='segnalazione',
            name='foto2',
            field=models.ImageField(blank=True, null=True, upload_to='foto/%Y/%m/%d/', verbose_name='Altra foto'),
        ),
        migrations.AddField(
            model_name='segnalazione',
            name='foto3',
            field=models.ImageField(blank=True, null=True, upload_to='foto/%Y/%m/%d/', verbose_name='Altra foto'),
        ),
        migrations.AlterField(
            model_name='segnalazione',
            name='categoria',
            field=models.ForeignKey(help_text='Seleziona la categoria e poi inserisci gli altri dati.', on_delete=django.db.models.deletion.CASCADE, to='segnala.categoria', verbose_name='Categoria *'),
        ),
        migrations.AlterField(
            model_name='segnalazione',
            name='cellulare',
            field=models.CharField(max_length=15, verbose_name='Numero di cellulare *'),
        ),
        migrations.AlterField(
            model_name='segnalazione',
            name='cognome',
            field=models.CharField(max_length=100, verbose_name='Cognome *'),
        ),
        migrations.AlterField(
            model_name='segnalazione',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='E-mail *'),
        ),
        migrations.AlterField(
            model_name='segnalazione',
            name='location',
            field=mapbox_location_field.models.LocationField(blank=True, map_attrs={'center': (10.515822538661212, 43.72580949521296), 'placeholder': 'Seleziona la posizione nella mappa.', 'style': 'mapbox://styles/mightysharky/cjwgnjzr004bu1dnpw8kzxa72'}, null=True, verbose_name='Indica sulla mappa la tua segnalazione oppure inserisci sotto i dettagli sulla posizione.'),
        ),
        migrations.AlterField(
            model_name='segnalazione',
            name='location_detail',
            field=models.CharField(blank=True, help_text="Aggiungere tutto quanto necessario perché l'operatore possa trovare la posizione esatta di quanto state segnalando.", max_length=250, null=True, verbose_name='Dettagli sulla posizione'),
        ),
        migrations.AlterField(
            model_name='segnalazione',
            name='nome',
            field=models.CharField(max_length=100, verbose_name='Nome *'),
        ),
        migrations.AlterField(
            model_name='segnalazione',
            name='testo',
            field=models.TextField(verbose_name='Dettaglio della segnalazione *'),
        ),
        migrations.AlterField(
            model_name='segnalazione',
            name='titolo',
            field=models.CharField(max_length=100, verbose_name='Titolo *'),
        ),
    ]