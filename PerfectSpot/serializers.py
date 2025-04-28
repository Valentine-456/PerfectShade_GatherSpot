from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Event

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
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'location', 'date', 'is_promoted', 'attendees_count']
        # 'creator' typically is set automatically from the request.user, so we might
        # not expose it as a writeable field here (depending on your logic).

    def create(self, validated_data):
        # The 'creator' should be the logged-in user, so we handle that in the view.
        return super().create(validated_data)

    def get_attendees_count(self, obj):
        return obj.attendees.count()

