from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Vibe, VibeLike
from .serializers import UserSerializer, VibeSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VibeViewSet(viewsets.ModelViewSet):
    serializer_class = VibeSerializer

    def get_queryset(self):
        return Vibe.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, _pk=None):
        vibe = self.get_object()
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