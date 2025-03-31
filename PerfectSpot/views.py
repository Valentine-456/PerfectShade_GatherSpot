from rest_framework import status, generics
from rest_framework.response import Response
# If using JWT:
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .models import CustomUser

class RegisterView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # If using JWT, create token:
            refresh = RefreshToken.for_user(user)

            return Response({
                "success": True,
                "message": "User registered successfully.",
                "data": {
                    "token": str(refresh.access_token),
                    "userID": user.id,
                    "email": user.email,
                    "username": user.username
                }
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Registration failed.",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # If using JWT:
            refresh = RefreshToken.for_user(user)

            return Response({
                "success": True,
                "message": "Logged in successfully.",
                "data": {
                    "token": str(refresh.access_token),
                    "userID": user.id,
                    "username": user.username
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Login failed.",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
