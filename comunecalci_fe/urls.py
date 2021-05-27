# -*- coding: utf-8 -*-
# Subject to the terms of the GNU AFFERO GENERAL PUBLIC LICENSE, v. 3.0. If a copy of the AGPL was not
# distributed with this file, You can obtain one at http://www.gnu.org/licenses/agpl.txt
#
# Author: Davide Galletti                davide   ( at )   c4k.it


from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from segnala import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('d', login_required(views.Debug.as_view()), name='d'),
    path('', views.AddSegnalazioneView.as_view(), name="home"),
    path('v/<int:id>/<str:t>', views.ValidazioneEmail.as_view(), name='v'),
    path('i', views.serve_image.as_view(), name='i'),
    path('s/<int:id>/<str:t>', views.VediSegnalazione.as_view(), name='s'),
    path('captcha/', include('captcha.urls')),
]
handler404 = 'segnala.views.page_not_found'
