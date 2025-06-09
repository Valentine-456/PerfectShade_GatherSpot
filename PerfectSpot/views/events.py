from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from PerfectSpot.serializers import EventSerializer, ReviewSerializer
from PerfectSpot.models import Event, Review
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken
import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateEventView(generics.GenericAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]  # Must be logged in to create an event

    # Allow unauthenticated GETs but require auth for anything else
    def get_permissions(self):
        from rest_framework.permissions import AllowAny
        if self.request.method == 'GET':
            return [AllowAny()]
        return [perm() for perm in self.permission_classes]

    @swagger_auto_schema(
        operation_description="List all events for the home screen.",
        responses={200: EventSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        # 1) Base queryset
        qs = Event.objects.all()

        # 2) Title-prefix filter (case-insensitive)
        title_prefix = request.query_params.get("title")
        if title_prefix:
            qs = qs.filter(title__istartswith=title_prefix)

        # 3) Promoted filter
        promoted_str = request.query_params.get("promoted")
        if promoted_str is not None:
            promoted = promoted_str.lower() in ("1", "true", "yes")
            qs = qs.filter(is_promoted=promoted)

        # 4) Apply your existing ordering
        events = qs.order_by('date')

        # 5) Serialize & return
        serializer = self.get_serializer(events, many=True)
        return Response({
            "success": True,
            "message": "Events retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new event. User must be authenticated.",
        responses={201: "Event created successfully", 400: "Validation error"}
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
                    "latitude": event.latitude,
                    "longitude": event.longitude,
                    "image_url": event.image_url,
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
    serializer_class = EventSerializer

    @swagger_auto_schema(
        operation_description="Get details for an event.",
        responses={
            200: openapi.Response(
                description="Event retrieved",
                schema=EventSerializer
            ),
            404: "Event not found"
        }
    )
    def get(self, request, pk):
        event = get_object_or_404(self.queryset, pk=pk)
        data = self.get_serializer(event).data
        return Response({
            "success": True,
            "message": "Event retrieved successfully.",
            "data": data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete an event by ID. Only the creator or staff can delete.",
        responses={
            200: "Event deleted successfully",
            403: "No permission",
            404: "Event not found"
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

class EditEventView(generics.GenericAPIView):
    """
    PATCH /events/{pk}/edit/  → Edit one or more fields of an event.
    Only the event's creator or staff may update.
    """
    serializer_class    = EventSerializer
    permission_classes  = [IsAuthenticated]
    queryset            = Event.objects.all()

    @swagger_auto_schema(
        operation_description="Edit an existing event; partial update allowed.",
        request_body=EventSerializer(partial=True),
        responses={
            200: openapi.Response(
                description="Event updated successfully",
                schema=EventSerializer
            ),
            400: "Validation error",
            403: "Not owner or staff",
            404: "Event not found"
        }
    )
    def patch(self, request, pk):
        # 1) Load the event or 404
        event = get_object_or_404(self.queryset, pk=pk)

        # 2) Permission: only creator or staff
        if event.creator != request.user and not request.user.is_staff:
            return Response({
                "success": False,
                "message": "You do not have permission to edit this event.",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)

        # 3) Apply partial update
        serializer = self.get_serializer(
            event, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()  # writes changes to the model
            return Response({
                "success": True,
                "message": "Event updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        # 4) Validation errors
        return Response({
            "success": False,
            "message": "Event update failed.",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PromoteEventView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        # must be the creator & an organization
        if event.creator != request.user or request.user.user_type != 'organization':
            return Response({
                "success": False,
                "message": "Only the organizing account can promote this event.",
                "data": None
            }, status=403)

        event.is_promoted = True
        event.save(update_fields=['is_promoted'])

        return Response({
            "success": True,
            "message": "Event promoted.",
            "data": {"eventID": event.id, "isPromoted": True}
        })



class RSVPEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if request.user in event.attendees.all():
            event.attendees.remove(request.user)
            is_attending = False
            message = "You are no longer attending."
        else:
            event.attendees.add(request.user)
            is_attending = True
            message = "You are now attending!"

        return Response({
            "success": True,
            "message": message,
            "data": {
                "attendees_count": event.attendees.count(),
                "is_attending": is_attending,
            }
        }, status=200)

class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(event_id=self.kwargs['pk'])


# — Add a new review to an event —
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        serializer.save(event=event, reviewer=self.request.user)


# — Edit an existing review (only the reviewer can) —
class ReviewUpdateView(generics.UpdateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'review_id'

    def get_queryset(self):
        # Only allow the author to edit their review
        return Review.objects.filter(
            event_id=self.kwargs['pk'],
            reviewer=self.request.user
        )


# — Delete a review (only the reviewer can) —
class ReviewDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'review_id'

    def get_queryset(self):
        return Review.objects.filter(
            event_id=self.kwargs['pk'],
            reviewer=self.request.user
        )
        
class CreateStripeCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user

        if user in event.attendees.all():
            return Response({"success": False, "message": "Already attending."}, status=400)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price_data": {
                "currency": "usd",
                "unit_amount": 1500,
                "product_data": {"name": f"Ticket for {event.title}"},
            },
                "quantity": 1,
    }],
    success_url = f"{settings.FRONTEND_URL}/event-success/{event.id}?session_id={{CHECKOUT_SESSION_ID}}",
    cancel_url=f"{settings.FRONTEND_URL}/events/{event.id}",
    metadata={"user_id": user.id},
)

        return Response({"id": session.id})
    
class ConfirmCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        session_id = request.data.get("session_id")
        if not session_id:
            return Response({"error": "Missing session ID"}, status=400)

        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status != "paid":
                return Response({"success": False, "message": "Payment not completed"}, status=400)

            event = get_object_or_404(Event, pk=pk)
            event.attendees.add(request.user)

            return Response({"success": True, "message": "You are now attending!"})
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)
