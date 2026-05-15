from typing import TypedDict


class DefaultSnippet(TypedDict):
    start_seconds: int
    end_seconds: int

class TrackData(TypedDict):
    track_id: str
    title: str
    artist: str
    cover_url: str
    stream_url: str
    default_snippet: DefaultSnippet