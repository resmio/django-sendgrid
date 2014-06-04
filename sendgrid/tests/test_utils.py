from django.test import TestCase
from django.core import mail

from sendgrid.utils import SendgridEmailMessage, SendgridEmailMultiAlternatives
from sendgrid.models import Email

import json


class UtilTestCase(TestCase):
    def setUp(self):
        self.email_data = {'subject': 'Test Subject',
                           'body': 'Hi, I am a test body',
                           'from_email': 'email@example.com',
                           'to': ('other_email@example.com', )}

    def test_django_email(self):
        message = mail.EmailMessage(**self.email_data)
        message.send()
        # this email should not have a UUID
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, self.email_data['subject'])
        self.assertNotIn('X-SMTPAPI', mail.outbox[0].extra_headers)

    def test_django_multipart(self):
        message = mail.EmailMultiAlternatives(**self.email_data)
        message.send()
        # this email should not have a UUID
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, self.email_data['subject'])
        self.assertNotIn('X-SMTPAPI', mail.outbox[0].extra_headers)

    def test_sendgrid_email(self):
        message = SendgridEmailMessage(**self.email_data)
        message.send()
        # this email should have a UUID
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, self.email_data['subject'])
        self.assertIn('X-SMTPAPI', mail.outbox[0].extra_headers)
        content = json.loads(mail.outbox[0].extra_headers['X-SMTPAPI'])
        self.assertIn('uuid', content['unique_args'])
        self.assertEqual(len(content['unique_args']['uuid']), 36)

    def test_sendgrid_multipart(self):
        message = SendgridEmailMultiAlternatives(**self.email_data)
        message.send()
        # this email should have a UUID
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, self.email_data['subject'])
        self.assertIn('X-SMTPAPI', mail.outbox[0].extra_headers)
        content = json.loads(mail.outbox[0].extra_headers['X-SMTPAPI'])
        self.assertIn('uuid', content['unique_args'])
        self.assertEqual(len(content['unique_args']['uuid']), 36)

    def test_sendgrid_email_object_attachment(self):
        # first send a message without an object
        message = SendgridEmailMessage(**self.email_data)
        message.send()
        mail_event_1 = Email.objects.get(uuid=message.uuid)
        self.assertEqual(mail_event_1.content_object, None)

        # now attach an object
        data = dict(self.email_data)
        data['obj'] = mail_event_1  # code re-use :)
        message = SendgridEmailMessage(**data)
        message.send()
        mail_event = Email.objects.get(uuid=message.uuid)
        self.assertEqual(mail_event.content_object, mail_event_1)

    def test_sendgrid_multipart_object_attachment(self):
        # first send a message without an object
        message = SendgridEmailMultiAlternatives(**self.email_data)
        message.send()
        mail_event_1 = Email.objects.get(uuid=message.uuid)
        self.assertEqual(mail_event_1.content_object, None)

        # now attach an object
        data = dict(self.email_data)
        data['obj'] = mail_event_1  # code re-use :)
        message = SendgridEmailMultiAlternatives(**data)
        message.send()
        mail_event = Email.objects.get(uuid=message.uuid)
        self.assertEqual(mail_event.content_object, mail_event_1)
