#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import reverse
from django import forms
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, ListView
from .models import Segnalazione
from captcha.fields import CaptchaField


def home(request):
    return render(request, 'home.html', {})

def thank_you(request, s_id):
    try:
        s = Segnalazione.objects.get(pk=s_id)
        # verifico un delta temporale dal tempo di creazione
        # se ce l'ho verifico l'IP
    except:
        raise Http404("Accesso non autorizzato")
    return render(request, 'segnala/thank_you.html', {'segnalazione': s})



class PlaceView(UpdateView):
    model = Segnalazione
    template_name = "segnala/place_form.html"
    success_url = "/"
    fields = ("nome", "cognome", "email", "cellulare", "titolo", "testo", "location", "address", "foto")


class SegnalazioneForm(forms.ModelForm):
    captcha = CaptchaField(label="Digita i caratteri nell'immagine seguente: ")

    class Meta:
        model = Segnalazione
        fields = ("nome", "cognome", "email", "cellulare", "titolo", "testo", "location", "address", "foto")
        #widgets = {'myfield1': forms.TextInput(attrs={'class': 'myfieldclass'}),}


class AddPlaceView(SuccessMessageMixin, CreateView):
    model = Segnalazione
    template_name = "segnala/place_form.html"
#    success_url = "/"
    success_message = 'La tua segnalazione è stata registrata correttamente. Riceverai un email all''indirizzo "%(email)". Per completare la segnalazione segui le istruzioni contenute nell''email.'
#    fields = ("nome", "cognome", "email", "cellulare", "titolo", "testo", "location", "address", "foto")
    form_class = SegnalazioneForm

    def get_success_url(self):
        return reverse('s', kwargs={'s_id': self.object.id})

    def get_success_message(self, cleaned_data):
        return '''La tua segnalazione è stata registrata correttamente. Riceverai un email all'indirizzo "%s". 
            Per completare la segnalazione segui le istruzioni contenute nell'email.''' % self.object.email