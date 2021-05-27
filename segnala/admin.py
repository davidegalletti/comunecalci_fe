# -*- coding: utf-8 -*-
# Subject to the terms of the GNU AFFERO GENERAL PUBLIC LICENSE, v. 3.0. If a copy of the AGPL was not
# distributed with this file, You can obtain one at http://www.gnu.org/licenses/agpl.txt
#
# Author: Davide Galletti                davide   ( at )   c4k.it


from django.contrib import admin

from segnala.models import Categoria, Segnalazione


class AdminSite(admin.AdminSite):
    site_header = 'Front-end segnalazioni Comune di Calci (PI)'
    site_title = 'Front-end segnalazioni Comune di Calci (PI)'


admin_site = AdminSite(name='admin')
admin_site.register(Categoria)
admin_site.register(Segnalazione)

admin.site.register(Categoria)
admin.site.register(Segnalazione)