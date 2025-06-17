from django.conf import settings
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class    = NotificationSerializer
    permission_classes  = [IsAuthenticated]

    def get_queryset(self):
        # uses related_name='notifications'
        return self.request.user.notifications.order_by("-created_at")