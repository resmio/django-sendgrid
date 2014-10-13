[![Build Status](https://api.travis-ci.org/resmio/django-sendgrid.png)](https://travis-ci.org/resmio/django-sendgrid)

Introduction
============

This django app enables you to send emails to sendgrid and receive callbacks to monitor the status of all your emails. 
You can also attach them to a related object in your own app. A signal will be dispatched every time a new callback is
received (and also when the email is created for the first time). We also provide helper classes which inherit from the 
email classes in `django.core.mail` which means you can transparently switch out the django classes with ours. 

Installation
============

1. `pip install django-sendgrid-webhook`
2. Add app to INSTALLED_APPS 

 ```python
 INSTALLED_APPS += 'sendgrid'
 ```
3. South compatibility (Django < 1.7)

 If you're using Django >= 1.7 you don't have to do anything, for users with older versions, South tries to use the new Django migrations instead of the South migrations. Please add the following code snippet to your settings:

 ```python
  SOUTH_MIGRATION_MODULES = {
         'sendgrid': 'sendgrid.south_migrations',
     }
 ```
4. Run `python manage.py syncdb` to install the new Email model
5. Include `sendgrid.urls` at some point in your url structure. E.g. in `/urls.py`:

 ```python
 # Sendgrid event hooks
 urlpatterns += patterns(
    '',
    url(r'^', include('sendgrid.urls')),
 )
 ```
 
 This will add the callback path `/sendgrid_callback/`.
6. Go to https://sendgrid.com/app and add the App `Event Notification`.
7. Configure the App to send the events you'd like to and add the Callback URL. If you included `sendgrid.urls` like 
 mentioned above it would be : `http://test.com/sendgrid_callback/`

Configuration
=============

Our classes in `sendgrid.utils` are inheriting from the default classes of `django.core.mail`, so you just need to 
configure your SMTP settings as shown in https://docs.djangoproject.com/en/dev/topics/email/#smtp-backend to use them. 

Configuration Options
---------------------

Currently we only have one configuration option which can be added to the django settings.

Adding `SENDGRID_EVENTS_IGNORE_MISSING = True` to your settings will silently ignore callbacks for emails which are 
sent without a UUID. This is very helpful because Sendgrid would otherwise receive a non-200 answer from our webhook
and would try to re-deliver the same message for 24h until giving up sending messages altogether. So unless you're 
very sure this will never happen, you should probably enable this.

Usage
=====

In theory you can send messages yourself by adding a UUID parameter to the `unique_args` parameter in the SMTP header 
`X-SMTPAPI` as specified in https://sendgrid.com/docs/API_Reference/SMTP_API/unique_arguments.html . But you can also 
save yourself the work and read the next section.

Sending emails (the easy way)
-----------------------------

`sendgrid.utils.SendgridEmailMessage` and `sendgrid.utils.SendgridEmailMultiAlternatives` can be used instead of the
Django versions in `django.core.mail`. In fact the easiest transition is to just replace every use of 
`from django.core.mail import EmailMessage` with `from sendgrid.utils import SendgridEmailMessage as EmailMessage`.
From then on every email you send will include an UUID parameter to track the callback, and a new instance of the 
model `sendgrid.models.Email` will be created and updated on every callback received.

You can also attach a related object to the `Email` object by passing an `obj` parameter in the `.send()` function of
`SendgridEmailMessage` or `SendgridEmailMultiAlternatives`.

Signals
-------

Every time a new object is created or a callback is received, the signal `sendgrid.signals.email_event` is dispatched.
See https://docs.djangoproject.com/en/dev/topics/signals/ for more details on Django signals.
