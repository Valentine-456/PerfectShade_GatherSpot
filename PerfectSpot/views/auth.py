from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from PerfectSpot.serializers import UserRegistrationSerializer, UserLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(
        operation_description="Register a new user (individual or organization).",
        responses={
            201: "User registered successfully",
            400: "Invalid data"
        }
    )

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

    @swagger_auto_schema(
        operation_description="Log in with username & password.",
        responses={
            200: "Logged in successfully",
            400: "Invalid credentials"
        }
    )

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