import uuid
import django

from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .signals import email_event


def _new_uuid():
    """Initialisation function for reference UUID."""

    return str(uuid.uuid4())


class Email(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    email = models.CharField(_('addressee'), max_length=512)
    event = models.CharField(_('event type'), max_length=32)
    reason = models.CharField(_('reason'), max_length=1024, default='')
    timestamp = models.DateTimeField(_('timestamp'))
    uuid = models.CharField(_('reference UUID'), max_length=64, default=_new_uuid, db_index=True)

    class Meta:
        index_together = (
            ('content_type', 'object_id'),
        )

    def __str__(self):
        return '%s: %s' % (self.email, self.event)

    def save(self, *args, **kwargs):
        # check if we're just creating the object
        if not self.pk:
            creation = True
        else:
            creation = False

        # then actually save it
        super(Email, self).save(*args, **kwargs)

        # and send out a proper signal with an instance of the saved model
        if creation:
            email_event.send(self)
