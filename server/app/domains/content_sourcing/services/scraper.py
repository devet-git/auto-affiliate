"""
Video Source Scraper — Extensible Multi-Source Architecture
============================================================
D-01 from 03-CONTEXT.md: Pluggable Interface (BaseVideoSource) so new
sources (TikTok, Douyin, YouTube Shorts, FB Reels) can be added via
config without rewriting core logic.

Usage:
    source = get_source("tiktok")
    videos = source.fetch_videos(keyword="áo thun nam", limit=10)
"""

from abc import ABC, abstractmethod
from typing import Any

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False


class BaseVideoSource(ABC):
    """
    Abstract base class for all video source crawlers.
    Each concrete source implements this interface.
    """

    @abstractmethod
    def fetch_videos(self, keyword: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Fetch a list of videos related to the given keyword.

        Args:
            keyword: Search keyword or product name (e.g. "áo khoác nam").
            limit: Maximum number of video results to return.

        Returns:
            List of dicts with keys:
                - url (str): Direct video URL or page URL
                - title (str): Video title / caption
                - thumbnail (str | None): Thumbnail URL
                - source (str): Source platform name
        """
        ...

    @property
    def source_name(self) -> str:
        """Human-readable name of this source platform."""
        return self.__class__.__name__


class TikTokSource(BaseVideoSource):
    """
    TikTok video source using yt-dlp for extraction.
    Does NOT download — only extracts metadata/URLs.
    """

    @property
    def source_name(self) -> str:
        return "tiktok"

    def fetch_videos(self, keyword: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Search TikTok for videos related to keyword.
        Returns metadata list without downloading files.
        """
        if not YT_DLP_AVAILABLE:
            raise ImportError("yt-dlp is required: pip install yt-dlp")

        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "playlist_items": f"1-{limit}",
        }
        search_url = f"https://www.tiktok.com/search?q={keyword}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(search_url, download=False)
                entries = info.get("entries", []) if info else []
                return [
                    {
                        "url": entry.get("url") or entry.get("webpage_url"),
                        "title": entry.get("title"),
                        "thumbnail": entry.get("thumbnail"),
                        "source": self.source_name,
                    }
                    for entry in entries
                ][:limit]
            except Exception as exc:
                # Log and return empty — non-fatal crawl failure
                print(f"[TikTokSource] Crawl error: {exc}")
                return []


class DouyinSource(BaseVideoSource):
    """
    Douyin (Chinese TikTok) video source stub using yt-dlp.
    Lower risk of rate-limiting than international TikTok.
    """

    @property
    def source_name(self) -> str:
        return "douyin"

    def fetch_videos(self, keyword: str, limit: int = 10) -> list[dict[str, Any]]:
        if not YT_DLP_AVAILABLE:
            raise ImportError("yt-dlp is required: pip install yt-dlp")

        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "playlist_items": f"1-{limit}",
        }
        search_url = f"https://www.douyin.com/search/{keyword}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(search_url, download=False)
                entries = info.get("entries", []) if info else []
                return [
                    {
                        "url": entry.get("url") or entry.get("webpage_url"),
                        "title": entry.get("title"),
                        "thumbnail": entry.get("thumbnail"),
                        "source": self.source_name,
                    }
                    for entry in entries
                ][:limit]
            except Exception as exc:
                print(f"[DouyinSource] Crawl error: {exc}")
                return []


# ─── Source Registry (D-01: add new sources here) ────────────────────────────
_SOURCE_REGISTRY: dict[str, type[BaseVideoSource]] = {
    "tiktok": TikTokSource,
    "douyin": DouyinSource,
}


def get_source(source_name: str) -> BaseVideoSource:
    """
    Factory: return a concrete BaseVideoSource by name.

    Args:
        source_name: Registered source key (e.g. "tiktok", "douyin").

    Returns:
        Instance of the matching source class.

    Raises:
        ValueError: If source_name is not in the registry.
    """
    source_class = _SOURCE_REGISTRY.get(source_name.lower())
    if not source_class:
        available = ", ".join(_SOURCE_REGISTRY.keys())
        raise ValueError(
            f"Source '{source_name}' not registered. Available: {available}"
        )
    return source_class()


def list_sources() -> list[str]:
    """Return all registered source names."""
    return list(_SOURCE_REGISTRY.keys())
