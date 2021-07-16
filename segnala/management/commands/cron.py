# -*- coding: utf-8 -*-
# Subject to the terms of the GNU AFFERO GENERAL PUBLIC LICENSE, v. 3.0. If a copy of the AGPL was not
# distributed with this file, You can obtain one at http://www.gnu.org/licenses/agpl.txt
#
# Author: Davide Galletti                davide   ( at )   c4k.it


import logging

from segnala.models import Segnalazione, Notifica
from django.core.management.base import BaseCommand

logger = logging.getLogger('cron')


def cron():
    try:
        Segnalazione.cron_notifiche_validazione()
    except Exception as ex:
        logger.error("cron_notifiche_validazione: %s" % str(ex))
    try:
        Notifica.cron_carica_notifiche_aggiornamenti()
    except Exception as ex:
        logger.error("cron_carica_notifiche_aggiornamenti: %s" % str(ex))
    try:
        Notifica.cron_notifiche_aggiornamenti()
    except Exception as ex:
        logger.error("cron_notifiche_aggiornamenti: %s" % str(ex))
    try:
        Segnalazione.cron_crea_redmine()
    except Exception as ex:
        logger.error("cron_crea_redmine: %s" % str(ex))


class Command(BaseCommand):
    help = '''Cron'''

    def handle(self, *args, **options):
        try:
            logger.info('INIZIO CRON')
            cron()
            logger.info('FINE CRON')
        except Exception as ex:
            logger.error("Cron: %s" % str(ex))
