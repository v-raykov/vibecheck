from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Vibe, VibeLike


class VibeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='other', password='password123')

        # Authenticate main test user
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password123'})
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_vibe(self):
        url = reverse('vibe-list')
        data = {'percentage': 80, 'emoji': '🚀', 'content': 'Testing vibes'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vibe.objects.count(), 1)
        self.assertEqual(Vibe.objects.get().user, self.user)

    def test_cannot_like_own_vibe(self):
        vibe = Vibe.objects.create(user=self.user, percentage=50, emoji='😐')
        url = reverse('vibe-like', kwargs={'pk': vibe.id})

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check through model count
        self.assertEqual(VibeLike.objects.filter(vibe=vibe).count(), 0)

    def test_toggle_like_others_vibe(self):
        other_vibe = Vibe.objects.create(user=self.other_user, percentage=100, emoji='🔥')
        url = reverse('vibe-like', kwargs={'pk': other_vibe.id})

        # First POST: Like
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(other_vibe.likes.count(), 1)
        self.assertEqual(response.data['status'], 'liked')

        # Second POST: Unlike
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(other_vibe.likes.count(), 0)
        self.assertEqual(response.data['status'], 'unliked')

    def test_vibe_serialization_includes_likes(self):
        other_vibe = Vibe.objects.create(user=self.other_user, percentage=90, emoji='📈')
        # Manually create a like from our user
        VibeLike.objects.create(user=self.user, vibe=other_vibe)

        url = reverse('vibe-detail', kwargs={'pk': other_vibe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 1)
        self.assertTrue(response.data['is_liked'])

    def test_unauthenticated_vibe_list(self):
        # Clear credentials
        self.client.credentials()
        url = reverse('vibe-list')
        response = self.client.get(url)

        # Should be 401 because of our DEFAULT_PERMISSION_CLASSES
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
