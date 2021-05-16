# -*- coding: utf-8 -*-

import logging

from segnala.models import Segnalazione
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.management.base import BaseCommand
from django.db import transaction
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def get_from_email():
    return settings.EMAIL_FROM_ADDRESS


def format_email_subject(subject):
    return subject


class EmailSender():
    def __init__(self, template_prefix):
        self.template_prefix = template_prefix

    def render_mail(self, email, context):
        """
        ### NOT USED YET
        Renders an e-mail to `email`.  `template_prefix` identifies the
        e-mail that is to be sent, e.g. "account/email/email_confirmation"
        """
        subject = render_to_string('{0}_subject.txt'.format(self.template_prefix),
                                   context)
        # remove superfluous line breaks
        subject = " ".join(subject.splitlines()).strip()
        subject = format_email_subject(subject)

        from_email = get_from_email()

        bodies = {}
        for ext in ['html', 'txt']:
            try:
                template_name = '{0}_message.{1}'.format(self.template_prefix, ext)
                bodies[ext] = render_to_string(template_name,
                                               context).strip()
            except TemplateDoesNotExist:
                if ext == 'txt' and not bodies:
                    # We need at least one body
                    raise
        if 'txt' in bodies:
            msg = EmailMultiAlternatives(subject,
                                         bodies['txt'],
                                         from_email,
                                         [email])
            if 'html' in bodies:
                msg.attach_alternative(bodies['html'], 'text/html')
        else:
            msg = EmailMessage(subject,
                               bodies['html'],
                               from_email,
                               [email])
            msg.content_subtype = 'html'  # Main content is now text/html
        return msg

    def send_mail(self, email, context):
        ### NOT USED YET
        msg = self.render_mail(email, context)
        msg.send()


def send_email():
    for s in Segnalazione.objects.filter(email_inviato=False, email_tentativo__lte=settings.MAX_EMAIL_ATTEMPTS):
        try:
            with transaction.atomic():
                # mando l'email
                pass

        except Exception as ex:
            logger.error("linee_prodotti: %s" % str(ex))



class Command(BaseCommand):
    help = '''Fixtures'''

    def handle(self, *args, **options):
        try:
            send_email()
        except Exception as ex:
            logger.error("unificazione_prodotti: %s" % str(ex))
