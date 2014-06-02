from django.core.mail import EmailMessage, EmailMultiAlternatives

import uuid
import json


class SendgridEmailMessage(EmailMessage):
    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, cc=None):
        super(SendgridEmailMessage, self).__init__(subject, body, from_email, to, bcc, connection, attachments,
                                                   headers, cc)
        self.extra_headers.update({
            'X-SMTPAPI': json.dumps({
                'unique_args': {
                    'uuid': str(uuid.uuid4())
                }
            })
        })


class SendgridEmailMultiAlternatives(EmailMultiAlternatives):
    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, cc=None):
        super(SendgridEmailMultiAlternatives, self).__init__(subject, body, from_email, to, bcc, connection,
                                                             attachments, headers, cc)
        self.extra_headers.update({
            'X-SMTPAPI': json.dumps({
                'unique_args': {
                    'uuid': str(uuid.uuid4())
                }
            })
        })
