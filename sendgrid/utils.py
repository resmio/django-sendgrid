from django.core.mail import EmailMessage, EmailMultiAlternatives

import uuid
import json
from datetime import datetime

import models


class SendgridEmailMessage(EmailMessage):
    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, cc=None):
        super(SendgridEmailMessage, self).__init__(subject, body, from_email, to, bcc, connection, attachments,
                                                   headers, cc)
        self.uuid = str(uuid.uuid4())
        self.extra_headers.update({
            'X-SMTPAPI': json.dumps({
                'unique_args': {
                    'uuid': self.uuid,
                }
            })
        })

    def send(self, fail_silently=False):
        ret = super(SendgridEmailMessage, self).send(fail_silently)
        models.Email.objects.create(uuid=self.uuid,
                                    email=str(self.to),
                                    timestamp=datetime.now(),
                                    event='initiated')
        return ret


class SendgridEmailMultiAlternatives(EmailMultiAlternatives):
    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, cc=None):
        super(SendgridEmailMultiAlternatives, self).__init__(subject, body, from_email, to, bcc, connection,
                                                             attachments, headers, cc)
        self.uuid = str(uuid.uuid4())
        self.extra_headers.update({
            'X-SMTPAPI': json.dumps({
                'unique_args': {
                    'uuid': self.uuid,
                }
            })
        })

    def send(self, fail_silently=False):
        ret = super(SendgridEmailMultiAlternatives, self).send(fail_silently)
        models.Email.objects.create(uuid=self.uuid,
                                    email=str(self.to),
                                    timestamp=datetime.now(),
                                    event='initiated')
        return ret
