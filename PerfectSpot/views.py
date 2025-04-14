from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .serializers import EventSerializer
from .models import CustomUser, Event
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserRegistrationSerializer, UserLoginSerializer, EventSerializer

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


class CreateEventView(generics.GenericAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]  # Must be logged in to create an event

    @swagger_auto_schema(
        operation_description="Create a new event. User must be authenticated.",
        responses={
            201: "Event created successfully",
            400: "Validation error"
        }
    )

    def post(self, request, *args, **kwargs):
        # The request.user will be the 'creator' of the event
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save(creator=request.user)  # pass the creator
            return Response({
                "success": True,
                "message": "Event created successfully.",
                "data": {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "location": event.location,
                    "date": event.date,
                    "is_promoted": event.is_promoted
                }
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Event creation failed.",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DeleteEventView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]  # Must be logged in
    queryset = Event.objects.all()

    @swagger_auto_schema(
        operation_description="Delete an event by ID. Only the creator or staff can delete.",
        responses={
            200: "Event deleted successfully",
            404: "Event not found",
            403: "No permission"
        }
    )

    def delete(self, request, pk):
        try:
            event = self.get_queryset().get(pk=pk)
        except Event.DoesNotExist:
            return Response({
                "success": False,
                "message": "Event not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        # Optional: Only allow the creator (or an admin) to delete
        if event.creator != request.user and not request.user.is_staff:
            return Response({
                "success": False,
                "message": "You do not have permission to delete this event.",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)

        event.delete()
        return Response({
            "success": True,
            "message": "Event deleted successfully.",
            "data": None
        }, status=status.HTTP_200_OK)
