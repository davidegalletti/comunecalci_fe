# -*- coding: utf-8 -*-
# Subject to the terms of the GNU AFFERO GENERAL PUBLIC LICENSE, v. 3.0. If a copy of the AGPL was not
# distributed with this file, You can obtain one at http://www.gnu.org/licenses/agpl.txt
#
# Author: Davide Galletti                davide   ( at )   c4k.it


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
