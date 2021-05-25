# Generated by Django 3.2.3 on 2021-05-22 16:20

from django.db import migrations
import mapbox_location_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('segnala', '0011_segnalazione_categoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='segnalazione',
            name='location',
            field=mapbox_location_field.models.LocationField(blank=True, map_attrs={'center': (10.515822538661212, 43.72580949521296), 'placeholder': 'Seleziona la posizione nella mappa.', 'style': 'mapbox://styles/mightysharky/cjwgnjzr004bu1dnpw8kzxa72'}, null=True, verbose_name='Posizione ed indirizzo'),
        ),
    ]