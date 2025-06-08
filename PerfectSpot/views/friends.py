from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from PerfectSpot.models import CustomUser
from PerfectSpot.serializers import FriendDataResponseSerializer, FriendshipStatusSerializer, UserSummarySerializer
from PerfectSpot.models import FriendRequest
from PerfectSpot.serializers import FriendRequestSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
      request_obj = self.get_object()

      if request_obj.to_user != request.user:
        return Response(status=status.HTTP_403_FORBIDDEN)

      from_user = request_obj.from_user
      to_user = request_obj.to_user

    # ✅ Create the mutual friendship
      from_user.friends.add(to_user)
      to_user.friends.add(from_user)

    # ✅ Delete the request
      request_obj.delete()

      return Response({"status": "accepted"})

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        request_obj = self.get_object()
        request_obj.delete()
        return Response({"status": "declined"})

    @action(detail=True, methods=["post"], url_path='cancel')
    def cancel(self, request, pk=None):
        try:
            request_obj = FriendRequest.objects.get(pk=pk)
        except FriendRequest.DoesNotExist:  
            return Response({"detail": "Request not found"}, status=status.HTTP_404_NOT_FOUND)
        if request_obj.from_user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        request_obj.delete()
        return Response({"status": "canceled"})

class FriendshipStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        current_user = request.user
        target_user = get_object_or_404(CustomUser, id=user_id)

        # List of friends for the profile being viewed
        friends = target_user.friends.all()

        # Check request relationship between current and target
        sent = FriendRequest.objects.filter(from_user=current_user, to_user=target_user).first()
        received = FriendRequest.objects.filter(from_user=target_user, to_user=current_user).first()
        # incoming = FriendRequest.objects.filter(to_user=current_user)

        # Determine relationship status
        if target_user in current_user.friends.all():
            status = "friends"
            request_id = None
        elif sent:
            status = "sent"
            request_id = sent.id
        elif received:
            status = "received"
            request_id = received.id
        else:
            status = "none"
            request_id = None

        serializer = FriendDataResponseSerializer(target_user)
        data = serializer.data
        # data = {
        #     "username": target_user.get_full_name() or target_user.username,
        #     "login": target_user.username,
        #     "friends": friends,
        #     "interests": list(target_user.interests.all().values_list("name", flat=True)), # or however you store it
        #     "events_count": target_user.events.count(),  # if reverse relationship exists
        #     "incoming": incoming,
        #     "status": status,
        #     "request_id": request_id,
        # }
        data["status"] = status
        data["request_id"] = request_id

        # serializer = FriendshipStatusSerializer(data)
        return Response(data)
      
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unfriend(request, user_id):
    current_user = request.user
    try:
        target_user = CustomUser.objects.get(id=user_id)
        if target_user in current_user.friends.all():
            current_user.friends.remove(target_user)
            target_user.friends.remove(current_user)
            return Response({'status': 'unfriended'})
        else:
            return Response({'detail': 'Not friends'}, status=status.HTTP_400_BAD_REQUEST)
    except CustomUser.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_friends(request):
    current_user = request.user
    friends = current_user.friends.all()
    serialized = UserSummarySerializer(friends, many=True)
    return Response({"data": serialized.data})
      
class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        serializer = FriendDataResponseSerializer(user)
        return Response(serializer.data)
