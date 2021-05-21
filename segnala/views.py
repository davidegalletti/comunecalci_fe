#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Subject to the terms of the GNU AFFERO GENERAL PUBLIC LICENSE, v. 3.0. If a copy of the AGPL was not
# distributed with this file, You can obtain one at http://www.gnu.org/licenses/agpl.txt
#
# Author: Davide Galletti                davide   ( at )   c4k.it


from django.urls import reverse
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.views.generic import CreateView, View, TemplateView
from .models import Segnalazione
from captcha.fields import CaptchaField


class SegnalazioneForm(forms.ModelForm):
    captcha = CaptchaField(label="Digita i caratteri nell'immagine seguente: ")

    class Meta:
        model = Segnalazione
        fields = ("nome", "cognome", "email", "cellulare", "titolo", "categoria", "testo", "location", "address", "foto")
        #widgets = {'myfield1': forms.TextInput(attrs={'class': 'myfieldclass'}),}

    class Media:
        js = ("js/segnalazione.js",)


class AddSegnalazioneView(SuccessMessageMixin, CreateView):
    model = Segnalazione
    template_name = "segnala/place_form.html"
    success_message = 'La tua segnalazione è stata registrata correttamente. Riceverai un email all''indirizzo "%(email)". Per completare la segnalazione segui le istruzioni contenute nell''email.'
    form_class = SegnalazioneForm

    def get_success_url(self):
        return reverse('s', kwargs={'id': self.object.id, 't': self.object.token_lettura})

    def get_success_message(self, cleaned_data):
        return '''La tua segnalazione è stata registrata correttamente. Riceverai un email all'indirizzo "%s". 
            Per completare la segnalazione segui le istruzioni contenute nell'email.''' % self.object.email

    def get_context_data(self, **kwargs):
        context = super(AddSegnalazioneView, self).get_context_data(**kwargs)
        context.update({'versione': settings.versio})


class ValidazioneEmail(TemplateView):
    template_name = 'segnala/validazione.html'

    def get_context_data(self, **kwargs):
        context = super(ValidazioneEmail, self).get_context_data(**kwargs)
        s_id = kwargs['id']
        token_validazione = kwargs['t']
        try:
            segnalazione = Segnalazione.objects.get(id = s_id)
        except:
            raise Http404("Accesso non autorizzato")
        if segnalazione.token_validazione == token_validazione:
            if segnalazione.stato == 'EMAIL_VALIDATO':
                messages.add_message(self.request, messages.WARNING, 'Hai già validato il tuo indirizzo di email. Verrai contattato in merito alla segnalazione fatta.')
            else:
                messages.add_message(self.request, messages.SUCCESS, 'Il tuo indirizzo di email è stato validato! Verrai contattato in merito alla segnalazione fatta.')
                segnalazione.stato = 'EMAIL_VALIDATO'
                segnalazione.save()

            # TODO: introdurre un limite di ore per la validazione
        else:
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
            Segnalazione.cron_notifiche()
            Segnalazione.cron_crea_redmine()
            return HttpResponse('cron ok')
        except Exception as ex:
            return HttpResponse('Errore cron: %s' % str(ex))


class Cron(View):
    def get(self, request):
        try:
            Segnalazione.cron_notifiche()
            Segnalazione.cron_crea_redmine()
            return HttpResponse('cron ok')
        except Exception as ex:
            return HttpResponse('Errore cron: %s' % str(ex))


class serve_image(View):
    def get(self, request):
        s_id = request.GET['id']
        token_foto = request.GET['t']
        try:
            segnalazione = Segnalazione.objects.get(id=s_id, token_foto=token_foto)
        except:
            raise Http404("Accesso non autorizzato")

        # with open('../filesystem_istrumentum/' + folder_notaio + '/' + subfolder01 + '/' + subfolder02 + '/tmp/' + ned_uuid + '/' + filename, 'rb') as pdf:
        with open('%s/%s%s' % (settings.BASE_DIR, settings.MEDIA_ROOT, segnalazione.foto.url[1:]), 'rb') as img:
            response = HttpResponse(img.read())
            response['Content-Type'] = 'image/jpeg'
            response['Content-Disposition'] = 'inline'
            # response['Content-Disposition'] = 'attachment'
            # response['Content-Disposition'] = 'inline; filename="some_file.pdf"'

        # pdf.close()
        return response
