from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Vibe, VibeLike
from .serializers import UserSerializer, VibeSerializer, MusicSearchQuerySerializer, MusicSuggestionsQuerySerializer, \
    MusicTrackDetailsQuerySerializer
from .services import MusicApiService


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "User created"}, status=status.HTTP_201_CREATED)


class CurrentUserView(APIView):
    def get(self, request):
        serializer = UserSerializer(data=request.user)
        return Response(serializer.data)


class VibeViewSet(viewsets.ModelViewSet):
    serializer_class = VibeSerializer

    def get_queryset(self):
        return Vibe.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        vibe = get_object_or_404(Vibe, pk=pk)
        user = request.user

        if vibe.user == user:
            return Response(
                {'error': 'You cannot vibe with your own post.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        like_qs = VibeLike.objects.filter(user=user, vibe=vibe)

        if like_qs.exists():
            like_qs.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)

        VibeLike.objects.create(user=user, vibe=vibe)
        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)


class MusicSuggestionsView(APIView):
    @extend_schema(parameters=[MusicSuggestionsQuerySerializer])
    def get(self, request):
        serializer = MusicSuggestionsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        percentage = serializer.validated_data.get('percentage', 50)

        if percentage <= 25:
            category = "cinematic"
        elif percentage <= 50:
            category = "lofi"
        elif percentage <= 75:
            category = "chill"
        else:
            category = "upbeat"

        tracks = MusicApiService.search_tracks(category, limit=5)
        return Response({"category_mapped": category, "tracks": tracks})


class MusicSearchView(APIView):
    @extend_schema(parameters=[MusicSearchQuerySerializer])
    def get(self, request):
        serializer = MusicSearchQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        query_string = serializer.validated_data.get('q').strip()

        tracks = MusicApiService.search_tracks(query_string, limit=5)
        return Response({"query": query_string, "tracks": tracks})

class MusicTrackDetailsView(APIView):
    @extend_schema(parameters=[MusicTrackDetailsQuerySerializer])
    def get(self, request):
        serializer = MusicTrackDetailsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        query_string = serializer.validated_data.get('track_id').strip()

        return Response(MusicApiService.get_track_details(query_string))
