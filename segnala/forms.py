#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Field, Submit, Fieldset, ButtonHolder


class SegnalaForm(forms.Form):
    nome = forms.CharField(required=True, label="Nome")
    cognome = forms.CharField(required=True, label="Cognome")
    titolo = forms.CharField(required=True, label="Titolo breve",
                             help_text='Es: "Asfalto via del Fienilaccio", "Parcheggio piazza Garibaldi", ... ')
    descrizione = forms.CharField(required=True, label="Descrizione dettagliata",
                             help_text='Descrivi dettagliatamente ')
    # categoria
    # mappa
    # allegati
    # captcha
    nic = forms.CharField(required=False, label=_("National id code"))
    from_date = forms.DateField(required=False, label=_("Born from"))
    to_date = forms.DateField(required=False, label=_("Born to"))

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.form_tag = True
        if kwargs['initial']['view_sensible_data']:
            self.helper.layout = Layout(
                InlineField('id'),
                InlineField('name'),
                InlineField('nic'),
                InlineField('from_date', css_class='dateinput'),
                InlineField('to_date', css_class='dateinput'),
                HTML("""<button type="submit" class="btn btn-primary"><i class="fa fa-search"></i> {0}</button>""".format(_("Search"))),
            )
        else:
            self.helper.layout = Layout(
                InlineField('id'),
                InlineField('last_name', type="hidden"),
                InlineField('first_name', type="hidden"),
                InlineField('nic', type="hidden"),
                InlineField('from_date', css_class='dateinput'),
                InlineField('to_date', css_class='dateinput'),
                HTML("""<button type="submit" class="btn btn-primary"><i class="fa fa-search"></i> {0}</button>""".format(_("Search"))),
            )


