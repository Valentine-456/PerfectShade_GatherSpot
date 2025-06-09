from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Event, FriendRequest, Review

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'user_type')

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            user_type=validated_data['user_type'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        data['user'] = user
        return data

class EventSerializer(serializers.ModelSerializer):
    attendees_count = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    is_attending = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'location', 'date', 'is_promoted','latitude',
                  'longitude','image_url','is_owner','attendees_count', 'is_attending']
        # 'creator' typically is set automatically from the request.user, so we might
        # not expose it as a writeable field here (depending on your logic).

    def create(self, validated_data):
        # The 'creator' should be the logged-in user, so we handle that in the view.
        return super().create(validated_data)
    
    def get_is_attending(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.attendees.filter(id=user.id).exists()

    def get_attendees_count(self, obj):
        return obj.attendees.count()

    def get_is_owner(self, obj):
        """
        Returns True if the current request user is the creator of this event.
        If no user is authenticated, return False.
        """
        request = self.context.get('request', None)
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return obj.creator_id == request.user.id



class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'created_at', 'reviewer']
        read_only_fields = ['id', 'created_at', 'reviewer']

class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username']
# (your existing EventSerializer stays here)
class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSummarySerializer(read_only=True)
    to_user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'created_at']

class FriendshipStatusSerializer(serializers.Serializer):
    friends = UserSummarySerializer(many=True)
    incoming = FriendRequestSerializer(many=True)
    status = serializers.ChoiceField(choices=['none', 'sent', 'received', 'friends'])
    request_id = serializers.IntegerField(required=False)
    
class SearchResultUserSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'status']

    def get_status(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return "none"

        user = request.user

        if obj == user:
            return "self"

        if user.friends.filter(id=obj.id).exists():
            return "friends"
        if FriendRequest.objects.filter(from_user=user, to_user=obj).exists():
            return "sent"
        if FriendRequest.objects.filter(from_user=obj, to_user=user).exists():
            return "received"

        return "none"
    
class FriendDataResponseSerializer(serializers.ModelSerializer):
    login = serializers.SerializerMethodField()
    interests = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    friends = UserSummarySerializer(many=True, read_only=True)
    events_count = serializers.SerializerMethodField()
    
    incoming = FriendRequestSerializer(source='received_requests', many=True, read_only=True)
    outgoing = FriendRequestSerializer(source='sent_requests', many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'login', 'interests', 'friends', 'events_count', 'incoming', 'outgoing', ]
        # Add any other fields you use in your profile frontend
    def get_login(self, obj):
        return obj.username

    def get_events_count(self, obj):
        return obj.events.count()