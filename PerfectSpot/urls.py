from django.urls import path
from PerfectSpot.views.auth import LoginView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="Register"),
    path("login/", LoginView.as_view(), name="Login")
]