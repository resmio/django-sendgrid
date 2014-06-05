from django.test import TestCase, Client
from django.conf import settings

import json

from sendgrid import utils, models


class BaseTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.email_data = {'subject': 'Test Subject',
                           'body': 'Hi, I am a test body',
                           'from_email': 'email@example.com',
                           'to': ('other_email@example.com', )}
        super(BaseTest, self).setUp()


class ViewTestCase(BaseTest):
    def test_callback_view(self):
        """ Test email callback.
        """
        message = utils.SendgridEmailMessage(**self.email_data)
        message.send()

        # test initial email state
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'initiated')

        # simulate callback by sendgrid
        response = self.client.post('/sendgrid_callback/',
                                    data=json.dumps([{
                                        'email': 'other_email@example.com',
                                        'uuid': message.uuid,
                                        'event': 'processed',
                                        'timestamp': '123456789',
                                    }, ]),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # this should have modified the existing email model
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'processed')

    def test_callback_view_error(self):
        """ Test the callback view with erroneous data.
        """
        message = utils.SendgridEmailMessage(**self.email_data)
        message.send()

        # test initial email state
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'initiated')

        # simulate callback by sendgrid
        with self.assertRaises(models.Email.DoesNotExist):
            self.client.post('/sendgrid_callback/',
                             data=json.dumps([{'email': 'other_email@example.com',
                                               'uuid': '333',
                                               'event': 'processed',
                                               'timestamp': '123456789', }, ]),
                             content_type='application/json')

        # nothing should have changed
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'initiated')

    def test_callback_with_missing_data(self):
        """ Test the callback view with erroneous data.
        """
        message = utils.SendgridEmailMessage(**self.email_data)
        message.send()

        # test initial email state
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'initiated')

        # simulate callback by sendgrid
        with self.assertRaises(KeyError):
            self.client.post('/sendgrid_callback/',
                             data=json.dumps([{'email': 'other_email@example.com',
                                               'event': 'processed',
                                               'timestamp': '123456789', }, ]),
                             content_type='application/json')

        # nothing should have changed
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'initiated')

    def test_wrong_transition(self):
        """ Test what happens if we try to do a wrong state transition
        """
        message = utils.SendgridEmailMessage(**self.email_data)
        message.send()

        # test initial email state
        self.assertEqual(models.Email.objects.count(), 1)
        _mail = models.Email.objects.all()[0]
        self.assertEqual(_mail.event, 'initiated')

        _mail.event = 'bounce'
        _mail.save()

        # simulate callback by sendgrid
        response = self.client.post('/sendgrid_callback/',
                                    data=json.dumps([{
                                        'email': 'other_email@example.com',
                                        'uuid': message.uuid,
                                        'event': 'processed',
                                        'timestamp': '123456789',
                                    }, ]),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # nothing should have changed
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'bounce')

    def test_state_transitions(self):
        """ Test normal state transitions.
        """
        message = utils.SendgridEmailMessage(**self.email_data)
        message.send()

        # test initial email state
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'initiated')

        # simulate callback by sendgrid
        response = self.client.post('/sendgrid_callback/',
                                    data=json.dumps([{
                                        'email': 'other_email@example.com',
                                        'uuid': message.uuid,
                                        'event': 'processed',
                                        'timestamp': '123456789',
                                    }, ]),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # this should have modified the existing email model
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'processed')

        # simulate next callback by sendgrid
        response = self.client.post('/sendgrid_callback/',
                                    data=json.dumps([{
                                        'email': 'other_email@example.com',
                                        'uuid': message.uuid,
                                        'event': 'delivered',
                                        'timestamp': '123459999',
                                    }, ]),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # this should have modified the existing email model
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'delivered')

    def test_wrong_saved_state(self):
        """ Test what happens if we saved a non-existent state in our email
        """
        message = utils.SendgridEmailMessage(**self.email_data)
        message.send()

        # test initial email state
        self.assertEqual(models.Email.objects.count(), 1)
        _mail = models.Email.objects.all()[0]
        self.assertEqual(_mail.event, 'initiated')

        _mail.event = 'bacon'
        _mail.save()

        # simulate callback by sendgrid
        with self.assertRaises(KeyError):
            self.client.post('/sendgrid_callback/',
                             data=json.dumps([{'email': 'other_email@example.com',
                                               'uuid': message.uuid,
                                               'event': 'processed',
                                               'timestamp': '123456789', }, ]),
                             content_type='application/json')


class ViewTZTestCase(ViewTestCase):
    """ Test explicitly with USE_TZ enabled.
    """
    def setUp(self):
        self._old_use_tz = settings.USE_TZ
        settings.USE_TZ = True
        super(ViewTZTestCase, self).setUp()

    def tearDown(self):
        settings.USE_TZ = self._old_use_tz
        super(ViewTZTestCase, self).tearDown()


class ViewNoTZTestCase(ViewTestCase):
    """ Test explicitly with USE_TZ disabled.
    """
    def setUp(self):
        self._old_use_tz = settings.USE_TZ
        settings.USE_TZ = False
        super(ViewNoTZTestCase, self).setUp()

    def tearDown(self):
        settings.USE_TZ = self._old_use_tz
        super(ViewNoTZTestCase, self).tearDown()


class IgnoreMissingTestCase(BaseTest):
    """ Test cases for SENDGRID_EVENTS_IGNORE_MISSING enabled.
    """
    def setUp(self):
        super(IgnoreMissingTestCase, self).setUp()
        settings.SENDGRID_EVENTS_IGNORE_MISSING = True

    def tearDown(self):
        del settings.SENDGRID_EVENTS_IGNORE_MISSING
        super(IgnoreMissingTestCase, self).tearDown()

    def test_callback_view_lenient_errors(self):
        """ Test callback using a non-existent, malformed UUID.
        """
        message = utils.SendgridEmailMessage(**self.email_data)
        message.send()

        # test initial email state
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'initiated')

        # simulate callback by sendgrid
        response = self.client.post('/sendgrid_callback/',
                                    data=json.dumps([{
                                        'email': 'other_email@example.com',
                                        'uuid': '333',
                                        'event': 'processed',
                                        'timestamp': '123456789',
                                    }, ]),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # nothing should have changed
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'initiated')

    def test_callback_with_missing_data(self):
        """ Test callback with missing data (no UUID).

        This is the default case if emails are not sent with our Classes
        """
        message = utils.SendgridEmailMessage(**self.email_data)
        message.send()

        # test initial email state
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'initiated')

        # simulate callback by sendgrid
        response = self.client.post('/sendgrid_callback/',
                                    data=json.dumps([{
                                        'email': 'other_email@example.com',
                                        'event': 'processed',
                                        'timestamp': '123456789',
                                    }, ]),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # nothing should have changed
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'initiated')

    def test_wrong_saved_state(self):
        """ Test what happens if we saved a non-existent state in our email
        """
        message = utils.SendgridEmailMessage(**self.email_data)
        message.send()

        # test initial email state
        self.assertEqual(models.Email.objects.count(), 1)
        _mail = models.Email.objects.all()[0]
        self.assertEqual(_mail.event, 'initiated')

        _mail.event = 'bacon'
        _mail.save()

        # simulate callback by sendgrid
        response = self.client.post('/sendgrid_callback/',
                                    data=json.dumps([{
                                        'email': 'other_email@example.com',
                                        'uuid': message.uuid,
                                        'event': 'processed',
                                        'timestamp': '123456789',
                                    }, ]),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # nothing should have changed
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.Email.objects.all()[0].event, 'bacon')
