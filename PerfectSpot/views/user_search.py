from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q

from PerfectSpot.serializers import SearchResultUserSerializer, UserSummarySerializer

User = get_user_model()

class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get("q", "")
        if not query:
            return Response({"results": []})

        users = User.objects.filter(
            Q(username__icontains=query)
        ).exclude(id=request.user.id)[:10]

        serializer = SearchResultUserSerializer(users, many=True, context={"request": request})
        return Response({"results": serializer.data})