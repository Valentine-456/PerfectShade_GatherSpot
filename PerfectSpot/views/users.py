from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from ..serializers import CustomUserSerializer

class UserListView(generics.ListAPIView):
    queryset           = get_user_model().objects.all()
    serializer_class   = CustomUserSerializer
    permission_classes = [IsAuthenticated]