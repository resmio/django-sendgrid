import uuid
import json

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
from django.utils.timezone import utc

from datetime import datetime

from .models import Email


class SendgridEmailMessage(EmailMessage):
    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, cc=None, obj=None):
        super(SendgridEmailMessage, self).__init__(subject, body, from_email, to, bcc, connection, attachments,
                                                   headers, cc)
        self.obj = obj
        self.uuid = str(uuid.uuid4())

        # Update the X-SMTPAPI header with our unique arguments (or create it)
        if headers is not None and headers.get('X-SMTPAPI'):
            try:
                api_dict = json.loads(headers['X-SMTPAPI'])
            except ValueError:
                api_dict = {}
        else:
            api_dict = {}
        unique_args = api_dict.setdefault('unique_args', {})
        unique_args['uuid'] = self.uuid

        self.extra_headers.update({
            'X-SMTPAPI': json.dumps(api_dict)
        })

    def send(self, fail_silently=False):
        ret = super(SendgridEmailMessage, self).send(fail_silently)
        if settings.USE_TZ:
            now = datetime.utcnow().replace(tzinfo=utc)
        else:
            now = datetime.now()

        data = {'uuid': self.uuid,
                'email': str(self.to),
                'timestamp': now,
                'event': 'initiated', }
        if self.obj:  # Work around for django < 1.7 because it doesn't support assigning None to generic FKs
            data.update({'content_object': self.obj, })
        Email.objects.create(**data)
        return ret


class SendgridEmailMultiAlternatives(EmailMultiAlternatives):
    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, cc=None, obj=None):
        super(SendgridEmailMultiAlternatives, self).__init__(subject, body, from_email, to, bcc, connection,
                                                             attachments, headers, cc)
        self.obj = obj
        self.uuid = str(uuid.uuid4())

        # Update the X-SMTPAPI header with our unique arguments (or create it)
        if headers is not None and headers.get('X-SMTPAPI'):
            try:
                api_dict = json.loads(headers['X-SMTPAPI'])
            except ValueError:
                api_dict = {}
        else:
            api_dict = {}
        unique_args = api_dict.setdefault('unique_args', {})
        unique_args['uuid'] = self.uuid

        self.extra_headers.update({
            'X-SMTPAPI': json.dumps(api_dict)
        })

    def send(self, fail_silently=False):
        ret = super(SendgridEmailMultiAlternatives, self).send(fail_silently)
        if settings.USE_TZ:
            now = datetime.utcnow().replace(tzinfo=utc)
        else:
            now = datetime.now()

        data = {'uuid': self.uuid,
                'email': str(self.to),
                'timestamp': now,
                'event': 'initiated', }
        if self.obj:  # Work around for django < 1.7 because it doesn't support assigning None to generic FKs
            data.update({'content_object': self.obj, })
        Email.objects.create(**data)
        return ret
