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
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SendgridHook, self).dispatch(*args, **kwargs)

    @staticmethod
    def post(request):
        response = json.loads(request.body)
        for event in response:
            try:
                email = Email.objects.get(uuid=event['uuid'])
                email.email = event['email']
                email.event = event['event']
                timestamp = datetime.datetime.fromtimestamp(int(event['timestamp']))
                if settings.USE_TZ:
                    timestamp = timestamp.utcnow().replace(tzinfo=utc)
                email.timestamp = timestamp
                email.save()
                signals.email_event.send(email)
            except Email.DoesNotExist:
                if not getattr(settings, 'SENDGRID_EVENTS_IGNORE_MISSING', False):
                    raise

        return HttpResponse('Thanks!')
