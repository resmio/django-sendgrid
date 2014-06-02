from django.test import TestCase, Client

import json

from sendgrid import utils, models


class ViewTestCase(TestCase):
    def setUp(self):
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

        # simulate callback by sengrid
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
