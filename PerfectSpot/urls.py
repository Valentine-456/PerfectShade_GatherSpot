# PerfectSpot/urls.py
from django.urls import path
from PerfectSpot.views.auth import RegisterView, LoginView
from PerfectSpot.views.events import DeleteEventView, CreateEventView


urlpatterns = [
    path('signup', RegisterView.as_view(), name='signup'),
    path('signin', LoginView.as_view(), name='signin'),
path('events', CreateEventView.as_view(), name='create_event'),
    path('events/<int:pk>', DeleteEventView.as_view(), name='delete_event'),
]
