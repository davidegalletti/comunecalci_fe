#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Subject to the terms of the GNU AFFERO GENERAL PUBLIC LICENSE, v. 3.0. If a copy of the AGPL was not
# distributed with this file, You can obtain one at http://www.gnu.org/licenses/agpl.txt
#
# Author: Davide Galletti                davide   ( at )   c4k.it

import logging

from django.urls import reverse
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView, View, TemplateView
from segnala.models import Segnalazione, Categoria
from captcha.fields import CaptchaField

logger = logging.getLogger('segnala')


class SegnalazioneForm(forms.ModelForm):
    captcha = CaptchaField(label="Digita i caratteri nell'immagine: ")

    def __init__(self, *args, **kwargs):
        super(SegnalazioneForm, self).__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.filter(attiva=True)

    def clean(self):
        cleaned_data = super(SegnalazioneForm, self).clean()
        if not (cleaned_data['location'] or cleaned_data['location_detail']):
            raise forms.ValidationError("Inserire la posizione selezionandola dalla mappa o digitare l'indirizzo o i dettagli della posizione nella casella di testo sotto la mappa.")
        if not cleaned_data['location']:
            # CENTRO DI CALCI SECONDO GEONAMES:
            if len(cleaned_data['location_detail']) < 8:
                raise forms.ValidationError(
                    "La descrizione della posizione deve essere più dettagliata. Inserire 8 caratteri o più.")
        else:
            lat_centro_di_calci = 10.51831
            lon_centro_di_calci = 43.72364
            lat = float(cleaned_data['location'].split(',')[0])
            lon = float(cleaned_data['location'].split(',')[1])
            delta_ammesso = 0.04
            if abs(lat_centro_di_calci-lat)>delta_ammesso or abs(lon_centro_di_calci-lon)>delta_ammesso:
                raise forms.ValidationError(
                    "La posizione indicata è troppo distante dal comune di Calci. Selezionare una posizione dentro i "
                    "confini comunali.")

    class Meta:
        model = Segnalazione
        fields = ("categoria", "nome", "cognome", "email", "cellulare", "titolo", "testo", "location", "location_detail", "address", "foto")

    class Media:
        js = ("js/segnalazione.js",)


class AddSegnalazioneView(SuccessMessageMixin, CreateView):
    model = Segnalazione
    template_name = "segnala/place_form.html"
    success_message = 'La tua segnalazione è stata registrata correttamente. Riceverai un email all''indirizzo "%(email)". Per completare la segnalazione segui le istruzioni contenute nell''email.'
    form_class = SegnalazioneForm

    def form_valid(self, form):
        self.object = form.save()
        # registro 'HTTP_X_FORWARDED_FOR' se disponibile
        if 'HTTP_X_FORWARDED_FOR' in self.request.META:
            self.object.extra_data = {'HTTP_X_FORWARDED_FOR': self.request.META['HTTP_X_FORWARDED_FOR']}
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('s', kwargs={'id': self.object.id, 't': self.object.token_lettura})

    def get_success_message(self, cleaned_data):
        return '''La tua segnalazione è stata registrata correttamente. Riceverai un email all'indirizzo "%s". 
            Per completare la segnalazione segui le istruzioni contenute nell'email.''' % self.object.email

    def get_context_data(self, **kwargs):
        context = super(AddSegnalazioneView, self).get_context_data(**kwargs)
        ## PATCH https://github.com/simon-the-shark/django-mapbox-location-field/issues/38
        if 'cleaned_data' in context['form']:
            posizione_zero = float(context['form'].cleaned_data['location'].split(',')[0])
            posizione_uno = float(context['form'].cleaned_data['location'].split(',')[1])
            context['form'].cleaned_data['location'] = '%s,%s' % (posizione_uno, posizione_zero)
            context.update({'versione': settings.VERSIONE})
        return context


class ValidazioneEmail(TemplateView):
    template_name = 'segnala/validazione.html'

    def get_context_data(self, **kwargs):
        context = super(ValidazioneEmail, self).get_context_data(**kwargs)
        s_id = kwargs['id']
        token_validazione = kwargs['t']
        try:
            segnalazione = Segnalazione.objects.get(id = s_id)
        except Exception as ex:
            logger.warning('Tentativo di validare email con parametro id segnalazione errat %s: %s' % (s_id, str(ex)))
            raise Http404("Accesso non autorizzato")
        if segnalazione.token_validazione == token_validazione:
            if segnalazione.stato == 'EMAIL_VALIDATO':
                messages.add_message(self.request, messages.WARNING, 'Hai già validato il tuo indirizzo di email. Verrai contattato in merito alla segnalazione fatta.')
            else:
                messages.add_message(self.request, messages.SUCCESS, 'Il tuo indirizzo di email è stato validato! Verrai contattato in merito alla segnalazione fatta.')
                segnalazione.stato = 'EMAIL_VALIDATO'
                segnalazione.save()
            # TODO: vogliamo introdurre un limite di ore per la validazione?
        else:
            logger.warning('Tentativo di validare email con parametro token segnalazione errato %s' % token_validazione)
            raise Http404("Accesso non autorizzato")
        context.update({'segnalazione': segnalazione})
        return context


class VediSegnalazione(TemplateView):
    template_name = 'segnala/vedi_segnalazione.html'

    def get_context_data(self, **kwargs):
        context = super(VediSegnalazione, self).get_context_data(**kwargs)
        s_id = kwargs['id']
        token_lettura = kwargs['t']
        try:
            segnalazione = Segnalazione.objects.get(id = s_id)
        except:
            raise Http404("Accesso non autorizzato")
        if segnalazione.token_lettura != token_lettura:
            raise Http404("Accesso non autorizzato")
        context.update({'segnalazione': segnalazione})
        return context


def page_not_found(request, exception):
    return render(request, '404.html', {'exception': str(exception)}, status=404)


class Debug(View):
    def get(self, request):
        try:
            from .models import Notifica
            #Segnalazione.cron_notifiche_validazione()
            Segnalazione.cron_crea_redmine()
            #Notifica.cron_notifiche_aggiornamenti()
            # from redminelib import Redmine
            # redmine = Redmine(settings.REDMINE_ENDPOINT, key=settings.REDMINE_KEY, version=settings.REDMINE_VERSION)
            # kw = {'cf_%s' % settings.REDMINE_CF_INVIARE_EMAIL: 1}
            # i = redmine.issue.filter(**kw, include=['journals'])
            # v = redmine.issue.filter(**kw)[0].custom_fields[0].value
            # id = redmine.issue.filter(cf_1='0')[0].custom_fields[0].id
            ip = ''
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                ip = request.META['HTTP_X_FORWARDED_FOR']
                logger.warning('Invocata view debug HTTP_X_FORWARDED_FOR %s' % ip)
            if 'REMOTE_ADDR' in request.META:
                ip = request.META['REMOTE_ADDR']
                logger.warning('Invocata view debug REMOTE_ADDR %s' % ip)
            return HttpResponse('debug %s' % ip)
            # Segnalazione.cron_notifiche()
            # bSegnalazione.cron_crea_redmine()
        except Exception as ex:
            logger.error('Errore view debug: %s' % str(ex))
            return HttpResponse('Errore view debug: %s' % str(ex))


class ServeImage(View):
    def get(self, request):
        s_id = request.GET['id']
        token_foto = request.GET['t']
        try:
            segnalazione = Segnalazione.objects.get(id=s_id, token_foto=token_foto)
        except:
            raise Http404("Accesso non autorizzato")

        with open('%s/%s%s' % (settings.BASE_DIR, settings.MEDIA_ROOT, segnalazione.foto.url[1:]), 'rb') as img:
            response = HttpResponse(img.read())
            response['Content-Type'] = 'image/jpeg'
            response['Content-Disposition'] = 'inline'

        return response
