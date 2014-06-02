from django.conf.urls import url

import views

urlpatterns = [
    url(r'^sendgrid_callback/$', views.SendgridHook.as_view()),
]
