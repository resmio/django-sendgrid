from django.test import TestCase, Client
from django.conf import settings

import json

from sendgrid import utils, models


class ViewTestCase(TestCase):
    def setUp(self):
        super(ViewTestCase, self).setUp()
        self.client = Client()
        self.email_data = {'subject': 'Test Subject',
                           'body': 'Hi, I am a test body',
                           'from_email': 'email@example.com',
                           'to': ('other_email@example.com', )}

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


class ViewTZTestcase(ViewTestCase):
    """ Test explicitly with USE_TZ enabled
    """
    def setUp(self):
        self._old_use_tz = settings.USE_TZ
        settings.USE_TZ = True
        super(ViewTZTestcase, self).setUp()

    def tearDown(self):
        settings.USE_TZ = self._old_use_tz


class ViewNoTZTestcase(ViewTestCase):
    """ Test explicitly with USE_TZ disabled
    """
    def setUp(self):
        self._old_use_tz = settings.USE_TZ
        settings.USE_TZ = False
        super(ViewNoTZTestcase, self).setUp()

    def tearDown(self):
        settings.USE_TZ = self._old_use_tz
