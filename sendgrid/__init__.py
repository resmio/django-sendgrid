"""A small django app around sendgrid and its webhooks"""

from utils import SendgridEmailMessage, SendgridEmailMultiAlternatives
from models import Email
from signals import email_event

__version__ = '0.1.0'
__all__ = ('SendgridEmailMessage', 'SendgridEmailMultiAlternatives', 'Email', 'email_event')
