from __future__ import annotations

import re

import requests

from materia_content_studio.config import Settings
from materia_content_studio.services.mock_data import mock_instagram_posts

GRAPH_BASE = "https://graph.facebook.com/v22.0"
HASHTAG_PATTERN = re.compile(r"#\w+")


class InstagramService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def fetch_recent_posts(self, use_mock_on_error: bool = True) -> list[dict]:
        if not self.settings.has_instagram_credentials:
            return mock_instagram_posts()

        params = {
            "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
            "access_token": self.settings.instagram_access_token,
            "limit": 50,
        }

        posts: list[dict] = []
        try:
            response = requests.get(
                f"{GRAPH_BASE}/{self.settings.instagram_business_account_id}/media",
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            for item in response.json().get("data", []):
                caption = item.get("caption", "")
                media_type = item.get("media_type", "IMAGE")
                posts.append(
                    {
                        "external_id": item.get("id"),
                        "posted_at": item.get("timestamp"),
                        "caption": caption,
                        "post_type": self._normalize_post_type(media_type),
                        "media_url": item.get("thumbnail_url") or item.get("media_url") or "",
                        "permalink": item.get("permalink", ""),
                        "hashtags": HASHTAG_PATTERN.findall(caption),
                        "metrics": {
                            "likes": item.get("like_count"),
                            "comments": item.get("comments_count"),
                        },
                    }
                )
        except requests.RequestException:
            if use_mock_on_error:
                return mock_instagram_posts()
            raise
        return posts

    @staticmethod
    def _normalize_post_type(media_type: str) -> str:
        mapping = {
            "VIDEO": "REEL",
            "CAROUSEL_ALBUM": "CAROUSEL",
            "IMAGE": "POST",
        }
        return mapping.get(media_type, media_type)
