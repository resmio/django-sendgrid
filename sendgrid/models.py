from django.db import models


class EmailEvent(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    email = models.CharField(max_length=512)
    event = models.CharField(max_length=32)
    timestamp = models.DateTimeField()
    uuid = models.CharField(max_length=64, default=lambda: str(uuid.uuid4()))

    def __unicode__(self):
        return '%s: %s' % (self.email, self.event)
