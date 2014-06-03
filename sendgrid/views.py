from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils.timezone import utc

import json
import datetime

from .models import Email
import signals


class SendgridHook(View):
    @csrf_exempt
    def post(self, request):
        response = json.loads(request.body)
        for event in response:
            email = Email.objects.get(uuid=event['uuid'])
            email.email = event['email']
            email.event = event['event']
            email.timestamp = datetime.datetime.fromtimestamp(int(event['timestamp'])).utcnow().replace(tzinfo=utc)
            email.save()
            signals.email_event.send(email)
        return HttpResponse('Thanks!')
