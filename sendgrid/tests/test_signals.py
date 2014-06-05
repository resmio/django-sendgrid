from django.test import TestCase, Client

from sendgrid import utils, signals

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
        data = []

        def email_event_handler(sender, signal):
            data.append((sender, signal, ))

        signals.email_event.connect(email_event_handler)

        # check if we received signals
        self.assertEqual(len(data), 0)
        message = utils.SendgridEmailMessage(**self.email_data)
        message.send()

        # check if we received the signal triggered by the email creation
        self.assertEqual(len(data), 1)

        response = self.client.post('/sendgrid_callback/',
                                    data=json.dumps([{
                                        'email': 'other_email@example.com',
                                        'uuid': message.uuid,
                                        'event': 'processed',
                                        'timestamp': '123456789',
                                    }, ]),
                                    content_type='application/json')

        # verify that we received a signal
        self.assertEqual(len(data), 2)
        self.assertEqual(data[1][0].event, 'processed')
        self.assertEqual(data[1][0].uuid, message.uuid)

        self.assertEqual(response.status_code, 200)
