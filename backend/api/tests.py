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


import json
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch


class MusicIntegrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='music_tester', password='password123')
        response = self.client.post(reverse('login'), {'username': 'music_tester', 'password': 'password123'})
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    @patch('api.services.MusicApiService._dispatch_request')
    def test_slider_matrix_deep_negative(self, mock_dispatch):
        mock_dispatch.return_value = [
            {"id": 101, "title": "Sad Strings", "artist": "Composer", "file_url": "http://test.mp3",
             "cover_url": "http://test.jpg"}]

        url = reverse('music-suggestions')
        response = self.client.get(url, {'percentage': 12})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['category_mapped'], 'cinematic')
        self.assertEqual(data['tracks'][0]['track_id'], '101')

    @patch('api.services.MusicApiService._dispatch_request')
    def test_slider_matrix_mild_negative(self, mock_dispatch):
        mock_dispatch.return_value = []
        url = reverse('music-suggestions')
        response = self.client.get(url, {'percentage': 40})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['category_mapped'], 'lofi')

    @patch('api.services.MusicApiService._dispatch_request')
    def test_slider_matrix_mild_positive(self, mock_dispatch):
        mock_dispatch.return_value = []
        url = reverse('music-suggestions')
        response = self.client.get(url, {'percentage': 65})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['category_mapped'], 'chill')

    @patch('api.services.MusicApiService._dispatch_request')
    def test_slider_matrix_deep_positive(self, mock_dispatch):
        mock_dispatch.return_value = []
        url = reverse('music-suggestions')
        response = self.client.get(url, {'percentage': 95})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['category_mapped'], 'upbeat')

    @patch('api.services.MusicApiService._dispatch_request')
    def test_slider_matrix_fallback_on_corrupt_input(self, mock_dispatch):
        mock_dispatch.return_value = []
        url = reverse('music-suggestions')
        response = self.client.get(url, {'percentage': 'not_a_number'})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['category_mapped'], 'lofi')

    @patch('api.services.MusicApiService._dispatch_request')
    def test_normalization_schema_matches_contract(self, mock_dispatch):
        mock_dispatch.return_value = [{
            "id": 999,
            "title": "Raw Track Title",
            "artist": "Raw Artist",
            "file_url": "https://freetouse.com/track.mp3",
            "cover_url": "https://freetouse.com/cover.jpg"
        }]

        url = reverse('music-suggestions')
        response = self.client.get(url, {'percentage': 100})
        data = json.loads(response.content.decode('utf-8'))
        track_payload = data['tracks'][0]

        self.assertEqual(track_payload['track_id'], '999')
        self.assertEqual(track_payload['title'], 'Raw Track Title')
        self.assertEqual(track_payload['artist'], 'Raw Artist')
        self.assertEqual(track_payload['stream_url'], 'https://freetouse.com/track.mp3')
        self.assertEqual(track_payload['cover_url'], 'https://freetouse.com/cover.jpg')
        self.assertEqual(track_payload['default_snippet']['start_seconds'], 30)
        self.assertEqual(track_payload['default_snippet']['end_seconds'], 50)

    @patch('api.services.MusicApiService._dispatch_request')
    def test_text_search_with_valid_query(self, mock_dispatch):
        mock_dispatch.return_value = [
            {"id": 202, "title": "Rainy Day", "artist": "Lofi King", "file_url": "http://test.mp3",
             "cover_url": "http://test.jpg"}]

        url = reverse('music-search')
        response = self.client.get(url, {'q': 'rainy'})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['query'], 'rainy')
        self.assertEqual(len(data['tracks']), 1)

    def test_text_search_empty_query_returns_empty_list(self):
        url = reverse('music-search')
        response = self.client.get(url, {'q': '   '})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['tracks'], [])

    @patch('urllib.request.urlopen')
    def test_service_network_timeout_graceful_handling(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection timed out")

        url = reverse('music-suggestions')
        response = self.client.get(url, {'percentage': 50})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['tracks'], [])
