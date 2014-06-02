from django.test import TestCase, Client

from sendgrid import utils

import json


class SignalTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.email_data = {'subject': 'Test Subject',
                           'body': 'Hi, I am a test body',
                           'from_email': 'email@example.com',
                           'to': ('other_email@example.com', )}

    def test_received_email(self):
        """ Test signals triggered by sendgrid callback.
        """
        message = utils.SendgridEmailMessage(**self.email_data)
        message.send()

        response = self.client.post('/sendgrid_callback/',
                                    data=json.dumps([{
                                        'email': 'other_email@example.com',
                                        'uuid': message.uuid,
                                        'event': 'processed',
                                        'timestamp': '123456789',
                                    }, ]),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
