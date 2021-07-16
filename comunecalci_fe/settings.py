# -*- coding: utf-8 -*-
# Subject to the terms of the GNU AFFERO GENERAL PUBLIC LICENSE, v. 3.0. If a copy of the AGPL was not
# distributed with this file, You can obtain one at http://www.gnu.org/licenses/agpl.txt
#
# Author: Davide Galletti                davide   ( at )   c4k.it


from . import keep_safe
from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = keep_safe.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'segnala.apps.SegnalaConfig',
    'mapbox_location_field',
    'bootstrap4',
    'captcha',
    'admin_ordering'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'comunecalci_fe.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'comunecalci_fe.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'USER': 'test_fe',
        'PASSWORD': keep_safe.DATABASE_PASSWORD,
        'NAME': keep_safe.DATABASE_NAME
    }
}

# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'it'

TIME_ZONE = 'Europe/Rome'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_ROOT = 'media/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
STATIC_ROOT = os.path.join(BASE_DIR, "media", "static")
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_FROM_ADDRESS = 'no_reply@comune.calci.pi.it'
MAX_EMAIL_ATTEMPTS = 3
EMAIL_HOST = keep_safe.EMAIL_HOST
EMAIL_PORT = keep_safe.EMAIL_PORT
EMAIL_USE_TLS = keep_safe.EMAIL_USE_TLS
EMAIL_HOST_USER = keep_safe.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = keep_safe.EMAIL_HOST_PASSWORD
HTTP_HOST = 'https://segnala.comune.calci.pi.it'

# PARAMETRI PER API REDMINE
REDMINE_ENDPOINT = keep_safe.REDMINE_ENDPOINT
REDMINE_VERSION = keep_safe.REDMINE_VERSION
REDMINE_KEY = keep_safe.REDMINE_KEY
REDMINE_PROJECT = 'TEST'
REDMINE_CF_INVIARE_EMAIL = '9'
REDMINE_CF_INVIA_LE_NOTE = '8'

# MAPBOX
MAPBOX_KEY = keep_safe.MAPBOX_KEY

# CAPTCHA
CAPTCHA_FONT_SIZE = 44

TOKEN_LENGTH = 16
from django.urls import reverse_lazy

LOGIN_URL = reverse_lazy('admin:login')

LOGGING_BASE_DIR = '/var/log/segnala/'
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s'
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        'cron': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGGING_BASE_DIR + 'cron_segnala_fe.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGGING_BASE_DIR + 'segnala_fe.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
        'cron': {
            'handlers': ['cron'],
            'propagate': True,
            'level': 'WARNING',
        },
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'WARNING',
        },
        'segnala': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'WARNING',
        },
    }
}

VERSIONE = '0.3.2'