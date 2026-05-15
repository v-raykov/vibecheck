from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Vibe


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class VibeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Vibe
        fields = ['id', 'user', 'percentage', 'emoji', 'content', 'likes_count', 'is_liked', 'created_at', 'track_id',
                  'snippet_start', 'snippet_end']

    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False


class MusicSuggestionsQuerySerializer(serializers.Serializer):
    percentage = serializers.IntegerField(required=False, default=50, min_value=0, max_value=100)


class MusicSearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=True, allow_blank=False)


class MusicTrackDetailsQuerySerializer(serializers.Serializer):
    track_id = serializers.CharField(required=True, allow_blank=False)
