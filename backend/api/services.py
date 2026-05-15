import json
import logging
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)


class MusicApiService:
    BASE_URL = "https://api.freetouse.com/v3/music"
    TIMEOUT_SECONDS = 5

    @classmethod
    def _normalize_tracks(cls, raw_response):
        if not raw_response or not isinstance(raw_response, dict):
            return []

        raw_tracks = raw_response.get("data")
        if not raw_tracks or not isinstance(raw_tracks, list):
            return []

        formatted_list = []
        for track in raw_tracks:
            if not isinstance(track, dict):
                continue

            artist_name = "Unknown Artist"
            artists_list = track.get("artists")
            if artists_list and isinstance(artists_list, list):
                first_artist = artists_list[0]
                if isinstance(first_artist, list) and len(first_artist) > 1:
                    artist_name = first_artist[1].get("name", "Unknown Artist")

            formatted_list.append({
                "track_id": str(track.get("id", "")),
                "title": track.get("title", "Unknown Title"),
                "artist": artist_name,
                "cover_url": track.get("thumbnails", {}).get("md", ""),
                "stream_url": track.get("files", {}).get("mp3", ""),
                "default_snippet": {
                    "start_seconds": 30,
                    "end_seconds": 50
                }
            })
        return formatted_list

    @classmethod
    def _dispatch_request(cls, endpoint_path, query_params):
        encoded_params = urllib.parse.urlencode(query_params)
        target_url = f"{cls.BASE_URL}/{endpoint_path}?{encoded_params}"

        request = urllib.request.Request(target_url, method="GET")

        try:
            with urllib.request.urlopen(request, timeout=cls.TIMEOUT_SECONDS) as response:
                if response.status == 200:
                    raw_data = response.read().decode('utf-8')
                    return json.loads(raw_data)
                return {}
        except Exception as e:
            logger.error(f"Network error communicating with Music API {endpoint_path}: {str(e)}")
            return {}

    @classmethod
    def search_tracks(cls, query_string, limit=5):
        params = {
            "query": query_string,
            "limit": limit
        }
        raw_data = cls._dispatch_request("tracks/search", params)
        return cls._normalize_tracks(raw_data)
