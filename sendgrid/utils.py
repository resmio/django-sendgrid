from django.core.mail import EmailMessage, EmailMultiAlternatives

import uuid
import json


class SendgridEmailMessage(EmailMessage):
    def __init__(self, *args, **kwargs):
        super(SendgridEmailMessage, self).__init__(*args, **kwargs)
        self.extra_headers.update({
            'X-SMTPAPI': json.dumps({
                'unique_args': {
                    'uuid': str(uuid.uuid4())
                }
            })
        })


class SendgridEmailMultiAlternatives(EmailMultiAlternatives):
    def __init__(self, *args, **kwargs):
        super(SendgridEmailMultiAlternatives, self).__init__(*args, **kwargs)
        self.extra_headers.update({
            'X-SMTPAPI': json.dumps({
                'unique_args': {
                    'uuid': str(uuid.uuid4())
                }
            })
        })
