# PerfectSpot/urls.py
from django.urls import path, include
from PerfectSpot.views.auth import RegisterView, LoginView
from PerfectSpot.views.events import (
    CreateEventView, DeleteEventView, RSVPEventView, EditEventView, PromoteEventView, ReviewCreateView, ReviewUpdateView, ReviewDestroyView, ReviewListView
)
from rest_framework.routers import DefaultRouter

from PerfectSpot.views.friends import FriendshipStatusView, UserProfileAPIView, my_friends, unfriend
from PerfectSpot.views.friends import FriendRequestViewSet
from PerfectSpot.views.user_search import UserSearchView
from PerfectSpot.views.auth import GoogleLoginView
router = DefaultRouter()
router.register(r"friend-requests", FriendRequestViewSet, basename="friend-request")


urlpatterns = [
    path('signup', RegisterView.as_view(), name='signup'),
    path('signin', LoginView.as_view(), name='signin'),
    path('events', CreateEventView.as_view(), name='create_event'),
    path('events/<int:pk>', DeleteEventView.as_view(), name='delete_event'),
    path('events/<int:pk>/rsvp/', RSVPEventView.as_view(), name='rsvp-event'),
    path('events/<int:pk>/edit/', EditEventView.as_view(), name='edit_event'),
    path('events/<int:pk>/promote/', PromoteEventView.as_view(), name='promote_event'),
    path("google-signin", GoogleLoginView.as_view(), name="google-signin"),
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
    path('users/<int:user_id>/friendship', FriendshipStatusView.as_view(), name='friendship-status'),
    path('users/<int:user_id>/unfriend', unfriend, name='unfriend'),
    path('me/friends', my_friends, name='my-friends'),
    path("users/search", UserSearchView.as_view(), name="user-search"),
    path("users/<int:user_id>/profile/", UserProfileAPIView.as_view(), name="user-profile-api"),
    path("", include(router.urls)),

]
