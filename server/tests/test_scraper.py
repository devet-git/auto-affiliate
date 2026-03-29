"""
Tests for Video Scraper Service (03-01-02)
"""

import importlib


def test_scraper_module_importable():
    module = importlib.import_module(
        "app.domains.content_sourcing.services.scraper"
    )
    assert module is not None


def test_base_video_source_exists():
    from app.domains.content_sourcing.services.scraper import BaseVideoSource
    assert BaseVideoSource is not None


def test_tiktok_source_exists():
    from app.domains.content_sourcing.services.scraper import TikTokSource
    assert TikTokSource is not None


def test_douyin_source_exists():
    from app.domains.content_sourcing.services.scraper import DouyinSource
    assert DouyinSource is not None


def test_tiktok_source_inherits_base():
    from app.domains.content_sourcing.services.scraper import BaseVideoSource, TikTokSource
    assert issubclass(TikTokSource, BaseVideoSource)


def test_get_source_factory():
    from app.domains.content_sourcing.services.scraper import get_source, TikTokSource
    source = get_source("tiktok")
    assert isinstance(source, TikTokSource)


def test_get_source_invalid_raises():
    from app.domains.content_sourcing.services.scraper import get_source
    try:
        get_source("invalid_source_xyz")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_list_sources_returns_list():
    from app.domains.content_sourcing.services.scraper import list_sources
    sources = list_sources()
    assert isinstance(sources, list)
    assert "tiktok" in sources
