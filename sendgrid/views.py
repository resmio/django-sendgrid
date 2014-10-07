from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils.timezone import utc
from django.conf import settings

import json
import datetime

from .models import Email
import signals


class SendgridHook(View):
    state_flow = {
        # Internal: Step 0
        'initiated': ('received', 'processed', 'dropped', 'delivered', 'bounce', 'open', 'click', 'unsubscribe',
                      'spamreport'),
        # Sendgrid: Step 1 - Receive
        'received': ('processed', 'dropped', 'delivered', 'bounce', 'open', 'click', 'unsubscribe', 'spamreport'),
        # Sendgrid: Step 2 - Process
        'processed': ('delivered', 'bounce', 'open', 'click', 'unsubscribe', 'spamreport'),
        'dropped': (),
        # Sendgrid: Step 3 - Deliver
        'delivered': ('open', 'click', 'unsubscribe', 'spamreport'),
        'bounce': (),
        # Sendgrid: Step 4 - Read
        'open': (),
        'click': (),
        'unsubscribe': (),
        'spamreport': (),
    }

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SendgridHook, self).dispatch(*args, **kwargs)

    def post(self, request):
        response = json.loads(request.body)
        for event in response:
            try:
                email = Email.objects.get(uuid=event['uuid'])
                email.email = event['email']
                email.reason = event.get('reason', '')

                try:
                    current_options = self.state_flow[email.event]
                    if event['event'] in current_options:
                        email.event = event['event']
                    else:
                        continue
                        # XXX log that callbacks arrive in the wrong order or are duplicates
                except KeyError:
                    if not getattr(settings, 'SENDGRID_EVENTS_IGNORE_MISSING', False):
                        raise
                    else:
                        pass
                        # XXX log that we are in an unknown state and most likely something is wrong
                        #     (or the API got updated)
                timestamp = datetime.datetime.fromtimestamp(int(event['timestamp']))
                if settings.USE_TZ:
                    timestamp = timestamp.utcnow().replace(tzinfo=utc)
                email.timestamp = timestamp
                email.save()
                signals.email_event.send(email)
            except (Email.DoesNotExist, KeyError):
                if not getattr(settings, 'SENDGRID_EVENTS_IGNORE_MISSING', False):
                    raise

        return HttpResponse('Thanks!')
