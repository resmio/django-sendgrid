import json
import datetime

from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils.timezone import utc
from django.conf import settings
from django.utils.module_loading import import_string

from .models import Email
from .signals import email_event


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


    @staticmethod
    def handle_single_event(event):
        try:
            email = Email.objects.get(uuid=event['uuid'])
            email.email = event['email']
            email.reason = event.get('reason', None)
            if email.reason is None:
                email.reason = ''

            try:
                current_options = SendgridHook.state_flow[email.event]
                if event['event'] in current_options:
                    email.event = event['event']
                else:
                    return
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
            email_event.send(email)
        except (Email.DoesNotExist, KeyError):
            if not getattr(settings, 'SENDGRID_EVENTS_IGNORE_MISSING', False):
                raise

    @staticmethod
    def handle_event(body):
        response = json.loads(body)

        alternative_single_event_handler = getattr(settings, 'SENDGRID_SINGLE_EVENT_HANDLER', False)

        for event in response:
            if alternative_single_event_handler:
                sendgrid_event_handler = import_string(alternative_single_event_handler)
                sendgrid_event_handler(event)
            else:
                SendgridHook.handle_single_event(event)


    def post(self, request):
        if getattr(settings, 'SENDGRID_EVENT_HANDLER', False):
            sendgrid_event_handler_path = getattr(settings, 'SENDGRID_EVENT_HANDLER', False)
            sendgrid_event_handler = import_string(sendgrid_event_handler_path)
            sendgrid_event_handler(request.body)
        else:
            SendgridHook.handle_event(request.body)

        return HttpResponse('Thanks!')
