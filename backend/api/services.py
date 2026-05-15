import json
import logging
import urllib.parse
import urllib.request
from typing import Any

from .types import TrackData

logger = logging.getLogger(__name__)


class MusicApiService:
    BASE_URL = "https://api.freetouse.com/v3/music"
    TIMEOUT_SECONDS = 5

    @classmethod
    def search_tracks(cls, query: str, limit: int = 5) -> list[TrackData]:
        raw = cls._dispatch_request("tracks/search", {"query": query, "limit": limit})
        return cls._normalize_tracks(raw)

    @classmethod
    def get_track_details(cls, track_id: str) -> TrackData | None:
        raw = cls._dispatch_request(f"tracks/{track_id}", None)
        track = cls._extract_single_track(raw)
        return cls._map_track(track) if track else None

    @classmethod
    def _dispatch_request(cls, endpoint_path: str, query_params: dict[str, Any] | None) -> dict[str, Any]:
        qs = "?" + urllib.parse.urlencode(query_params) if query_params else ""
        url = f"{cls.BASE_URL}/{endpoint_path}{qs}"
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=cls.TIMEOUT_SECONDS) as res:
                if res.status != 200:
                    return {}
                return json.loads(res.read().decode("utf-8"))
        except Exception as e:
            logger.error("Music API error %s: %s", endpoint_path, e)
            return {}

    @classmethod
    def _normalize_tracks(cls, raw: dict[str, Any]) -> list[TrackData]:
        if not isinstance(raw, dict):
            return []
        data = raw.get("data")
        if not isinstance(data, list):
            return []
        result = []
        for item in data:
            mapped = cls._map_track(item)
            if mapped:
                result.append(mapped)
        return result

    @staticmethod
    def _map_track(track: dict[str, Any]) -> TrackData | None:
        if not isinstance(track, dict):
            return None

        artist = "Unknown Artist"
        artists = track.get("artists")

        if isinstance(artists, list) and artists:
            first = artists[0]
            if isinstance(first, list) and len(first) > 1 and isinstance(first[1], dict):
                artist = str(first[1].get("name", artist))

        thumbnails = track.get("thumbnails")
        cover_url = thumbnails.get("md", "") if isinstance(thumbnails, dict) else ""

        files = track.get("files")
        stream_url = files.get("mp3", "") if isinstance(files, dict) else ""

        result: TrackData = {
            "track_id": str(track.get("id", "")),
            "title": str(track.get("title", "Unknown Title")),
            "artist": artist,
            "cover_url": cover_url,
            "stream_url": stream_url,
            "default_snippet": {
                "start_seconds": 30,
                "end_seconds": 50,
            },
        }
        return result

    @classmethod
    def _extract_single_track(cls, raw: dict[str, Any]) -> dict[str, Any] | None:
        if not isinstance(raw, dict):
            return None
        data = raw.get("data")
        if isinstance(data, dict):
            return data
        if isinstance(data, list) and data:
            return data[0]
        return None
