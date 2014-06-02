from django.test import TestCase
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core import mail

from sendgrid.utils import SendgridEmailMessage, SendgridEmailMultiAlternatives

import json


class UtilTestCase(TestCase):
    def test_django_email(self):
        message = EmailMessage(subject='Test Subject',
                               body='Hi, I am a test body',
                               from_email='email@example.com',
                               to=('other_email@example.com', ))
        message.send()
        # this email should not have a UUID
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        self.assertNotIn('X-SMTPAPI', mail.outbox[0].extra_headers)

    def test_django_multipart(self):
        message = EmailMultiAlternatives(subject='Test Subject',
                                         body='Hi, I am a test body',
                                         from_email='email@example.com',
                                         to=('other_email@example.com', ))
        message.send()
        # this email should not have a UUID
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        self.assertNotIn('X-SMTPAPI', mail.outbox[0].extra_headers)

    def test_sendgrid_email(self):
        message = SendgridEmailMessage(subject='Test Subject',
                                       body='Hi, I am a test body',
                                       from_email='email@example.com',
                                       to=('other_email@example.com', ))
        message.send()
        # this email should have a UUID
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        self.assertIn('X-SMTPAPI', mail.outbox[0].extra_headers)
        content = json.loads(mail.outbox[0].extra_headers['X-SMTPAPI'])
        self.assertIn('uuid', content['unique_args'])
        self.assertEqual(len(content['unique_args']['uuid']), 36)

    def test_sendgrid_multipart(self):
        message = SendgridEmailMultiAlternatives(subject='Test Subject',
                                                 body='Hi, I am a test body',
                                                 from_email='email@example.com',
                                                 to=('other_email@example.com', ))
        message.send()
        # this email should have a UUID
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        self.assertIn('X-SMTPAPI', mail.outbox[0].extra_headers)
        content = json.loads(mail.outbox[0].extra_headers['X-SMTPAPI'])
        self.assertIn('uuid', content['unique_args'])
        self.assertEqual(len(content['unique_args']['uuid']), 36)
