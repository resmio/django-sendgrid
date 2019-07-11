from django.urls import path

from .views import SendgridHook

urlpatterns = [
    path('sendgrid_callback/', SendgridHook.as_view()),
]
