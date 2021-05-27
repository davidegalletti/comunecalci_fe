# -*- coding: utf-8 -*-
# Subject to the terms of the GNU AFFERO GENERAL PUBLIC LICENSE, v. 3.0. If a copy of the AGPL was not
# distributed with this file, You can obtain one at http://www.gnu.org/licenses/agpl.txt
#
# Author: Davide Galletti                davide   ( at )   c4k.it

import logging
# noinspection PyCompatibility
from secrets import token_hex
from django.conf import settings
from django.db import models
from django.db.models.deletion import CASCADE
from django.urls import reverse
from mapbox_location_field.models import LocationField, AddressAutoHiddenField
from .utils import EmailSender
from redminelib import Redmine

logger_cron = logging.getLogger('cron')
logger = logging.getLogger('segnala')

class TimeStampedModel(models.Model):
    """An abstract base class model that provides self-updating ``created`` and ``modified`` fields."""
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    redmine_id = models.PositiveIntegerField(db_index=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categorie'

    def __str__(self):
        return self.nome


class Segnalazione(TimeStampedModel):
    '''
        stati:
            INIZIALE: appena creata, va inviato l'email; potrebbe essere stato già fatto qualche tentativo di invio
            EMAIL_FALLITO: dopo settings.MAX_EMAIL_ATTEMPTS tentativi falliti di invio
            EMAIL_INVIATO: L'email è stato inviato ma non è ancora arrivata la validazione
            EMAIL_VALIDATO: L'utente ha cliccato sul link di validazione nell'email
            CREATO_IN_REDMINE: Dopo la validazione è stato creato in redmine
            Altri stati dipendenti dal flusso che vogliono implementare in Redmine
            es: ACCETTATO: il ticket in Redmine è stato accettato in quanto sensato
                SCARTATO:  il ticket in Redmine è stato scartato
                COMPLETATO:
    '''
    redmine_id = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    token_validazione = models.CharField(max_length=100, db_index=True)
    token_lettura = models.CharField(max_length=100, db_index=True, blank=True, default='')
    token_foto = models.CharField(max_length=100, db_index=True, blank=True, default='')
    # token_foto usato come chiave per accedere alla foto dall'esterno
    email = models.EmailField()
    email_tentativo = models.IntegerField(default=0)
    # quanti tentativi sono stati fatti di invio email
    stato = models.CharField(max_length=50, default='INIZIALE')

    cellulare = models.CharField("Numero di cellulare", max_length=15)
    location = LocationField(verbose_name='Posizione ed indirizzo',
        map_attrs={"style": "mapbox://styles/mightysharky/cjwgnjzr004bu1dnpw8kzxa72",
                   "placeholder": "Seleziona la posizione nella mappa.",
                   "center": (10.515822538661212, 43.72580949521296)}, blank=True, null=True)
    address = AddressAutoHiddenField(blank=True, null=True)
    titolo = models.CharField(max_length=100)
    testo = models.TextField()
    foto = models.ImageField(upload_to='foto/%Y/%m/%d/', blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, help_text='Seleziona la categoria e poi inserisci gli altri dati.')
    # https://docs.djangoproject.com/en/3.2/releases/3.1/#jsonfield-for-all-supported-database-backends
    extra_data = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Segnalazioni'

    def __str__(self):
        return 'Segnalazione del %s, stato %s, inviata da %s %s: "%s"' % (self.created, self.stato,
                                                                          ('%s %s' % (self.nome, self.cognome)),
                                                                          self.email, self.titolo)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.id:
            self.token_validazione = token_hex(settings.TOKEN_LENGTH)
            self.token_lettura = token_hex(settings.TOKEN_LENGTH)
            self.token_foto = token_hex(settings.TOKEN_LENGTH)
        super(Segnalazione, self).save(force_insert, force_update, using, update_fields)

    def invia_email_validazione(self):
        es = EmailSender('validazione')
        try:
            context = {
                'http_host': settings.HTTP_HOST,
                'segnalazione': self
            }
            self.email_tentativo += 1
            es.send_mail(self.email, 'Comune di Calci, segnalazione %s' % self.id, context)
            self.stato = 'EMAIL_INVIATO'
            self.save()
        except Exception as ex:
            if self.email_tentativo > settings.MAX_EMAIL_ATTEMPTS:
                self.stato = 'EMAIL_FALLITO'
                logger_cron.warning('Superato in massimo numero di tentativi (%s) di invio email per la segnalazione %s'
                                ' all\'indirizzo %s: %s' % (settings.MAX_EMAIL_ATTEMPTS,
                                                            self.id,
                                                            self.email,
                                                            str(ex)) )
            self.save()

    def crea_in_redmine(self):
        try:
            redmine = Redmine(settings.REDMINE_ENDPOINT, key=settings.REDMINE_KEY, version=settings.REDMINE_VERSION)
            redmine_project = redmine.project.get(settings.REDMINE_PROJECT)
            red_issue = redmine.issue.create(
                subject = self.titolo,
                description = '%s\n\n%s\n !%s!' % (self.testo, ('%s\n\n' % self.tag_mappa), self.foto_url),
                category_id = self.categoria.redmine_id,
                custom_fields = [
                    {'id': 1, 'value': self.nome},
                    {'id': 2, 'value': self.cognome},
                    {'id': 3, 'value': 'id=%s&t=%s' % (self.id, self.token_foto)},
                    {'id': 4, 'value': (self.location[0] if self.location else '')},
                    {'id': 5, 'value': (self.location[1] if self.location else '')},
                    {'id': 6, 'value': self.address},
                    {'id': 7, 'value': self.cellulare}
                ],
                project_id = redmine_project.id)
            self.stato = 'CREATO_IN_REDMINE'
            self.redmine_id = red_issue.id
            self.save()
        except Exception as ex:
            logger_cron.error('Errore creando in redmine la segnalazione %s: %s' % (self.id, str(ex)) )

    @property
    def tag_mappa(self):
        if self.location:
            return '{{leaflet_map(%s, %s, 17)}}\n{{leaflet_marker(%s, %s, %s)}}' % \
                   (self.location[1], self.location[0], self.location[1], self.location[0], self.titolo)
        return ''

    @property
    def foto_url(self):
        if self.foto:
            return '%s%s?id=%s&t=%s' % (settings.HTTP_HOST, reverse('i'), self.id, self.token_foto)
        return ''

    @classmethod
    def cron_notifiche(cls):
        for s in Segnalazione.objects.filter(stato='INIZIALE', email_tentativo__lt=settings.MAX_EMAIL_ATTEMPTS):
            s.invia_email_validazione()

    @classmethod
    def cron_crea_redmine(cls):
        for s in Segnalazione.objects.filter(stato='EMAIL_VALIDATO'):
            s.crea_in_redmine()


class Aggiornamento(TimeStampedModel):
    segnalazione = models.ForeignKey(Segnalazione, on_delete=CASCADE)
    testo = models.TextField()
    lat = models.DecimalField('Latitude', max_digits=10, decimal_places=8)
    lng = models.DecimalField('Longitude', max_digits=11, decimal_places=8)


class Foto(models.Model):
    aggiornamento = models.ForeignKey(Aggiornamento, on_delete=CASCADE)
    image = models.ImageField(upload_to='foto/%Y/%m/%d/')

