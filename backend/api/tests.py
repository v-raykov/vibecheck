from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Vibe, VibeLike

class VibeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='other', password='password123')

        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password123'})
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_vibe(self):
        url = reverse('vibe-list')
        data = {'percentage': 80, 'emoji': '🚀', 'content': 'Testing vibes'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vibe.objects.count(), 1)

        # Verify the list output includes the new vibe inside 'results'
        list_response = self.client.get(url)
        self.assertEqual(len(list_response.data['results']), 1)
        self.assertEqual(list_response.data['results'][0]['content'], 'Testing vibes')

    def test_cannot_like_own_vibe(self):
        vibe = Vibe.objects.create(user=self.user, percentage=50, emoji='😐')
        url = reverse('vibe-like', kwargs={'pk': vibe.id})

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(VibeLike.objects.filter(vibe=vibe).count(), 0)

    def test_toggle_like_others_vibe(self):
        other_vibe = Vibe.objects.create(user=self.other_user, percentage=100, emoji='🔥')
        url = reverse('vibe-like', kwargs={'pk': other_vibe.id})

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(other_vibe.likes.count(), 1)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(other_vibe.likes.count(), 0)

    def test_vibe_serialization_includes_likes(self):
        # Detail view is NOT paginated, so this test stays mostly the same
        other_vibe = Vibe.objects.create(user=self.other_user, percentage=90, emoji='📈')
        VibeLike.objects.create(user=self.user, vibe=other_vibe)

        url = reverse('vibe-detail', kwargs={'pk': other_vibe.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 1)
        self.assertTrue(response.data['is_liked'])

    def test_pagination_structure(self):
        # Create 11 vibes to trigger a second page (assuming PAGE_SIZE=10)
        for _ in range(11):
            Vibe.objects.create(user=self.other_user, percentage=50, emoji='🌊')

        url = reverse('vibe-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check for pagination keys
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertEqual(response.data['count'], 11)
        self.assertEqual(len(response.data['results']), 10)

    def test_unauthenticated_vibe_list(self):
        self.client.credentials()
        url = reverse('vibe-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)