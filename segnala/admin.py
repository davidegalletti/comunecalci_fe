# -*- coding: utf-8 -*-
# Subject to the terms of the GNU AFFERO GENERAL PUBLIC LICENSE, v. 3.0. If a copy of the AGPL was not
# distributed with this file, You can obtain one at http://www.gnu.org/licenses/agpl.txt
#
# Author: Davide Galletti                davide   ( at )   c4k.it

from admin_ordering.admin import OrderableAdmin

from django.contrib import admin
from segnala.models import Categoria, Segnalazione
from mapbox_location_field.admin import MapAdmin

class SegnalazioneAdmin(MapAdmin):
    search_fields = ['nome', 'cognome', 'email', 'titolo', 'testo']
    list_filter = ['categoria', 'stato']


class CategoriaAdmin(OrderableAdmin, admin.ModelAdmin):
    ordering_field = "ordine"
    ordering_field_hide_input = True
    list_display = ["nome", "ordine"]
    list_editable = ["ordine"]
    exclude = ['ordine']


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Segnalazione, SegnalazioneAdmin)
