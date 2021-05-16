#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from django.db import models
from django.db.models.deletion import CASCADE
from mapbox_location_field.models import LocationField, AddressAutoHiddenField


class TimeStampedModel(models.Model):
    """An abstract base class model that provides self-updating ``created`` and ``modified`` fields."""
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Segnalazione(TimeStampedModel):
    redmine_id = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    token = models.CharField(max_length=100, db_index=True)
    email = models.EmailField()
    email_tentativo = models.IntegerField(default=0)
    # quanti tentativi sono stati fatti di invio email
    email_validato = models.BooleanField(default=False)
    email_inviato = models.BooleanField(default=False)
    cellulare = models.CharField("Numero di cellulare", max_length=15)
    location = LocationField(verbose_name='Posizione ed indirizzo',
        map_attrs={"style": "mapbox://styles/mightysharky/cjwgnjzr004bu1dnpw8kzxa72",
                   "placeholder": "Seleziona la posizione nella mappa.",
                   "center": (10.515822538661212, 43.72580949521296)})
    address = AddressAutoHiddenField()
    titolo = models.CharField(max_length=100)
    testo = models.TextField()
    foto = models.ImageField(upload_to='foto/%Y/%m/%d/', blank=True, null=True)


class Aggiornamento(TimeStampedModel):
    segnalazione = models.ForeignKey(Segnalazione, on_delete=CASCADE)
    testo = models.TextField()
    lat = models.DecimalField('Latitude', max_digits=10, decimal_places=8)
    lng = models.DecimalField('Longitude', max_digits=11, decimal_places=8)


class Foto(models.Model):
    aggiornamento = models.ForeignKey(Aggiornamento, on_delete=CASCADE)
    image = models.ImageField(upload_to='foto/%Y/%m/%d/')

