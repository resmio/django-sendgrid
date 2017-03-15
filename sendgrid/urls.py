from django.conf.urls import url

from .views import SendgridHook

urlpatterns = [
    url(r'^sendgrid_callback/$', SendgridHook.as_view()),
]
