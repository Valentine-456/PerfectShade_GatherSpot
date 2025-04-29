# PerfectSpot/urls.py
from django.urls import path
from PerfectSpot.views.auth import RegisterView, LoginView
from PerfectSpot.views.events import (
    CreateEventView, DeleteEventView, RSVPEventView, EditEventView, PromoteEventView, ReviewCreateView, ReviewUpdateView, ReviewDestroyView, ReviewListView
)


urlpatterns = [
    path('signup', RegisterView.as_view(), name='signup'),
    path('signin', LoginView.as_view(), name='signin'),
    path('events', CreateEventView.as_view(), name='create_event'),
    path('events/<int:pk>', DeleteEventView.as_view(), name='delete_event'),
    path('events/<int:pk>/rsvp/', RSVPEventView.as_view(), name='rsvp-event'),
    path('events/<int:pk>/edit/', EditEventView.as_view(), name='edit_event'),
    path('events/<int:pk>/promote/', PromoteEventView.as_view(), name='promote_event'),
    path(
        'events/<int:pk>/reviews/',
        ReviewListView.as_view(),
        name='list_reviews'
    ),
    path(
        'events/<int:pk>/reviews/add',
        ReviewCreateView.as_view(),
        name='add_review'
    ),
    path(
        'events/<int:pk>/reviews/<int:review_id>',
        ReviewUpdateView.as_view(),
        name='edit_review'
    ),
    path(
        'events/<int:pk>/reviews/<int:review_id>/delete',
        ReviewDestroyView.as_view(),
        name='delete_review'
    ),

]
