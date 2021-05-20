# -*- coding: utf-8 -*-

import logging

from segnala.models import Segnalazione
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


def cron():
    try:
        Segnalazione.cron_notifiche()
    except Exception as ex:
        logger.error("cron: %s" % str(ex))


class Command(BaseCommand):
    help = '''Cron'''

    def handle(self, *args, **options):
        try:
            cron()
        except Exception as ex:
            logger.error("Cron: %s" % str(ex))
