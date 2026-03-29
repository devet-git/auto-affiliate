"""
Tests for FFmpeg Deduplication Service (03-01-01)
"""

import importlib
import pytest


def test_ffmpeg_dedupe_module_importable():
    """The ffmpeg_dedupe module must be importable."""
    module = importlib.import_module(
        "app.domains.content_sourcing.services.ffmpeg_dedupe"
    )
    assert module is not None


def test_apply_light_dedupe_exists():
    from app.domains.content_sourcing.services.ffmpeg_dedupe import apply_light_dedupe
    assert callable(apply_light_dedupe)


def test_apply_deep_dedupe_exists():
    from app.domains.content_sourcing.services.ffmpeg_dedupe import apply_deep_dedupe
    assert callable(apply_deep_dedupe)


def test_apply_dedupe_dispatcher_exists():
    from app.domains.content_sourcing.services.ffmpeg_dedupe import apply_dedupe
    assert callable(apply_dedupe)


def test_dedupe_mode_constants():
    from app.domains.content_sourcing.services.ffmpeg_dedupe import (
        DEDUPE_MODE_LIGHT,
        DEDUPE_MODE_DEEP,
    )
    assert DEDUPE_MODE_LIGHT == "light"
    assert DEDUPE_MODE_DEEP == "deep"
