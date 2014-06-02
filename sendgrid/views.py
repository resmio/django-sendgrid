from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import json

from .models import Email


class SendgridHook(View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        response = json.loads(request.raw_post_data)
        for event in response:
            Email.objects.create(email=event['email'],
                                      event=event['event'],
                                      timestamp=event['timestamp'],
                                      uuid=event['uuid'])
        return HttpResponse('Thanks!')
