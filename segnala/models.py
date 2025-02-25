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
    ordine = models.SmallIntegerField(default=0, db_index=True)
    attiva = models.BooleanField(default=True)
    testo_di_aiuto = models.CharField(max_length=300, help_text='NON ANCORA USATO', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categorie'
        ordering = ['ordine']

    def __str__(self):
        return self.nome


class Segnalazione(TimeStampedModel):
    STATO = (
        ('INIZIALE', 'INIZIALE'),
        ('EMAIL_FALLITO', 'EMAIL_FALLITO'),
        ('EMAIL_INVIATO', 'EMAIL_INVIATO'),
        ('EMAIL_VALIDATO', 'EMAIL_VALIDATO'),
        ('CREATO_IN_REDMINE', 'CREATO_IN_REDMINE'),
    )
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
    nome = models.CharField(verbose_name="Nome *", max_length=100)
    cognome = models.CharField(verbose_name="Cognome *", max_length=100)
    token_validazione = models.CharField(max_length=100, db_index=True)
    token_lettura = models.CharField(max_length=100, db_index=True, blank=True, default='')
    token_foto = models.CharField(max_length=100, db_index=True, blank=True, default='')
    # token_foto usato come chiave per accedere alla foto dall'esterno
    email = models.EmailField(verbose_name="E-mail *")
    email_tentativo = models.IntegerField(default=0)
    # quanti tentativi sono stati fatti di invio email
    stato = models.CharField(max_length=50, default='INIZIALE', choices=STATO)

    cellulare = models.CharField("Numero di cellulare *", max_length=15)
    location = LocationField(verbose_name="Indica sulla mappa la tua segnalazione oppure inserisci sotto i dettagli "
                                          "sulla posizione.",
                             map_attrs={"style": "mapbox://styles/mightysharky/cjwgnjzr004bu1dnpw8kzxa72",
                                        "placeholder": "Seleziona la posizione nella mappa.",
                                        "center": (10.515822538661212, 43.72580949521296)}, blank=True, null=True)
    location_detail = models.CharField("Dettagli sulla posizione", max_length=250, blank=True, null=True,
                                       help_text="Aggiungere tutto quanto necessario perché l'operatore possa trovare la posizione esatta di quanto state segnalando.")
    address = AddressAutoHiddenField(blank=True, null=True)
    titolo = models.CharField(verbose_name="Titolo *", max_length=100)
    testo = models.TextField(verbose_name="Dettaglio della segnalazione *")
    foto = models.ImageField(upload_to='foto/%Y/%m/%d/', blank=True, null=True)
    foto2 = models.ImageField("Altra foto", upload_to='foto/%Y/%m/%d/', blank=True, null=True)
    foto3 = models.ImageField("Altra foto", upload_to='foto/%Y/%m/%d/', blank=True, null=True)
    categoria = models.ForeignKey(Categoria, verbose_name="Categoria *", on_delete=models.CASCADE,
                                  help_text='Seleziona la categoria e poi inserisci gli altri dati.')
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
                                                                str(ex)))
            self.save()

    @property
    def redmine_foto_description(self):
        foto = []
        foto_url = self.foto_url
        if self.foto:
            foto.append('!%s&n=1!' % foto_url)
        if self.foto2:
            foto.append('!%s&n=2!' % foto_url)
        if self.foto3:
            foto.append('!%s&n=3!' % foto_url)
        return '\n\n'.join(foto)

    def crea_in_redmine(self):
        try:
            logger_cron.info('Creo in redmine la Segnalazione %s' % self.id)
            redmine = Redmine(settings.REDMINE_ENDPOINT, key=settings.REDMINE_KEY, version=settings.REDMINE_VERSION)
            redmine_project = redmine.project.get(settings.REDMINE_PROJECT)
            red_issue = redmine.issue.create(
                subject=self.titolo,
                description='%s\n\n%s\n %s' % (self.testo, ('%s\n\n' % self.tag_mappa), self.redmine_foto_description),
                category_id=self.categoria.redmine_id,
                custom_fields=[
                    {'id': 1, 'value': self.nome},
                    {'id': 2, 'value': self.cognome},
                    {'id': 3, 'value': ('id=%s&t=%s' % (self.id, self.token_foto) if self.foto else '')},
                    {'id': 4, 'value': (self.location[0] if self.location else '')},
                    {'id': 5, 'value': (self.location[1] if self.location else '')},
                    {'id': 6, 'value': self.address},
                    {'id': 7, 'value': self.cellulare}
                ],
                project_id=redmine_project.id)
            self.stato = 'CREATO_IN_REDMINE'
            self.redmine_id = red_issue.id
            self.save()
        except Exception as ex:
            logger_cron.error('Errore creando in redmine la segnalazione %s: %s' % (self.id, str(ex)))

    @property
    def tag_mappa(self):
        if self.location:
            return '{{leaflet_map(%s, %s, 17)}}\n{{leaflet_marker(%s, %s, %s)}}' % \
                   (self.location[1], self.location[0], self.location[1], self.location[0], self.titolo)
        return ''

    @property
    def foto_url(self):
        return 'https://%s%s?id=%s&t=%s' % (settings.HTTP_HOST, reverse('i'), self.id, self.token_foto)

    @classmethod
    def cron_notifiche_validazione(cls):
        for s in Segnalazione.objects.filter(stato='INIZIALE', email_tentativo__lt=settings.MAX_EMAIL_ATTEMPTS):
            s.invia_email_validazione()

    @classmethod
    def cron_crea_redmine(cls):
        for s in Segnalazione.objects.filter(stato='EMAIL_VALIDATO'):
            s.crea_in_redmine()


class Notifica(TimeStampedModel):
    STATO = (
        ('INIZIALE', 'INIZIALE'),
        ('EMAIL_FALLITO', 'EMAIL_FALLITO'),
        ('EMAIL_INVIATO', 'EMAIL_INVIATO')
    )
    segnalazione = models.ForeignKey(Segnalazione, on_delete=models.CASCADE)
    journal_id = models.IntegerField(db_index=True)
    email_tentativo = models.IntegerField(default=0)
    # quanti tentativi sono stati fatti di invio email
    stato = models.CharField(max_length=50, default='INIZIALE', choices=STATO)
    testo_da_inviare = models.TextField()

    @classmethod
    def cron_carica_notifiche_aggiornamenti(cls):
        logger_cron.info('Inizio cron_carica_notifiche_aggiornamenti')
        redmine = Redmine(settings.REDMINE_ENDPOINT, key=settings.REDMINE_KEY, version=settings.REDMINE_VERSION)
        redmine_project = redmine.project.get(settings.REDMINE_PROJECT)
        kw = {'cf_%s' % settings.REDMINE_CF_INVIARE_EMAIL: 1}
        issues_con_notifiche = redmine.issue.filter(**kw, include=['journals'])
        logger_cron.info('len(issues_con_notifiche) %s' % len(issues_con_notifiche))
        for issue in issues_con_notifiche:
            for journal in issue.journals:
                notifica_da_inviare = False
                for detail in journal.details:
                    if detail['property'] == 'cf' and detail['name'] == settings.REDMINE_CF_INVIA_LE_NOTE \
                            and detail['new_value'] == '1':
                        # è una modifica che setta a True il flag INVIA_LE_NOTE ?
                        notifica_da_inviare = True
                        break
                if notifica_da_inviare:
                    # se non è già registrata la creo
                    if not Notifica.objects.filter(segnalazione__redmine_id=issue.id, journal_id=journal.id).exists():
                        try:
                            segnalazione = Segnalazione.objects.get(redmine_id=issue.id)
                            n = Notifica(segnalazione=segnalazione,
                                         journal_id=journal.id,
                                         testo_da_inviare=journal.notes)
                            n.save()
                        except Exception as ex:
                            logger_cron.error('Errore cercando la segnalazione il cui id su redmine è %s: %s' %
                                              (issue.id, str(ex)))
            kw = {'id': settings.REDMINE_CF_INVIARE_EMAIL, 'value': '0'}
            issue.custom_fields = [kw]
            issue.save()
        logger_cron.info('Fine cron_carica_notifiche_aggiornamenti')

    @classmethod
    def cron_notifiche_aggiornamenti(cls):
        for s in Notifica.objects.filter(stato='INIZIALE', email_tentativo__lt=settings.MAX_EMAIL_ATTEMPTS):
            s.invia_email_aggiornamento()

    def invia_email_aggiornamento(self):
        es = EmailSender('aggiornamento')
        try:
            context = {
                'http_host': settings.HTTP_HOST,
                'notifica': self
            }
            self.email_tentativo += 1
            es.send_mail(self.segnalazione.email, 'Comune di Calci, segnalazione "%s" (%s)' %
                         (self.segnalazione.titolo, self.segnalazione.id), context)
            self.stato = 'EMAIL_INVIATO'
            self.save()
        except Exception as ex:
            if self.email_tentativo > settings.MAX_EMAIL_ATTEMPTS:
                self.stato = 'EMAIL_FALLITO'
                logger_cron.warning('Superato in massimo numero di tentativi (%s) di invio email per la segnalazione %s'
                                    ' all\'indirizzo %s: %s' % (settings.MAX_EMAIL_ATTEMPTS,
                                                                self.id,
                                                                self.segnalazione.email,
                                                                str(ex)))
            self.save()

    class Meta:
        verbose_name_plural = 'Notifiche'


class Aggiornamento(TimeStampedModel):
    segnalazione = models.ForeignKey(Segnalazione, on_delete=CASCADE)
    testo = models.TextField()
    lat = models.DecimalField('Latitude', max_digits=10, decimal_places=8)
    lng = models.DecimalField('Longitude', max_digits=11, decimal_places=8)


class Foto(models.Model):
    aggiornamento = models.ForeignKey(Aggiornamento, on_delete=CASCADE)
    image = models.ImageField(upload_to='foto/%Y/%m/%d/')
