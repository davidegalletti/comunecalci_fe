"""comunecalci_fe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from segnala import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('d', views.Debug.as_view(), name='d'),
    path('', views.AddSegnalazioneView.as_view(), name="home"),
    path('v/<int:id>/<str:t>', views.ValidazioneEmail.as_view(), name='v'),
    path('i', views.serve_image.as_view(), name='i'),
    path('s/<int:id>/<str:t>', views.VediSegnalazione.as_view(), name='s'),
    path('captcha/', include('captcha.urls')),
]
handler404 = 'segnala.views.page_not_found'
