# -*- coding: utf-8 -*-
# Subject to the terms of the GNU AFFERO GENERAL PUBLIC LICENSE, v. 3.0. If a copy of the AGPL was not
# distributed with this file, You can obtain one at http://www.gnu.org/licenses/agpl.txt
#
# Author: Davide Galletti                davide   ( at )   c4k.it


from django.conf import settings
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string


class EmailSender():
    def __init__(self, template_prefix):
        self.template_prefix = template_prefix

    def render_mail(self, email, subject, context):
        """
        ### NOT USED YET
        Renders an e-mail to `email`.  `template_prefix` identifies the
        e-mail that is to be sent, e.g. "account/email/email_confirmation"
        """
        # remove superfluous line breaks
        subject = " ".join(subject.splitlines()).strip()

        from_email = settings.EMAIL_FROM_ADDRESS

        bodies = {}
        for ext in ['html', 'txt']:
            try:
                template_name = 'segnala/email/{0}.{1}'.format(self.template_prefix, ext)
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

    def send_mail(self, email, subject, context):
        ### NOT USED YET
        msg = self.render_mail(email, subject, context)
        msg.send()
