# Phase 03-01 Summary: Hot Video Crawler & Downloader

**Plan:** 03-01
**Phase:** 03 — Content Sourcing & Social Seeding
**Status:** Complete
**Completed:** 2026-03-29

## What Was Built

Extensible video sourcing infrastructure and FFmpeg-based deduplication engine for the content pipeline.

## Key Files Created

- `server/app/domains/content_sourcing/__init__.py` — domain package
- `server/app/domains/content_sourcing/services/__init__.py` — services sub-package
- `server/app/domains/content_sourcing/services/ffmpeg_dedupe.py` — Deduplication engine (light + deep modes)
- `server/app/domains/content_sourcing/services/scraper.py` — Extensible scraper with BaseVideoSource, TikTokSource, DouyinSource
- `server/tests/test_ffmpeg_dedupe.py` — Unit test stubs for dedupe module
- `server/tests/test_scraper.py` — Unit test stubs for scraper module

## Architectural Decisions Applied

- **D-01**: BaseVideoSource abstract class + _SOURCE_REGISTRY dict for zero-code source addition.
- **D-04**: Both DEDUPE_MODE_LIGHT (metadata strip) and DEDUPE_MODE_DEEP (hflip + 1.05x speed) implemented; `apply_dedupe()` dispatcher lets campaigns configure mode.

## Self-Check

- [x] `ffmpeg_dedupe.py` contains `apply_light_dedupe` with `map_metadata=-1`
- [x] `ffmpeg_dedupe.py` contains `apply_deep_dedupe` with `hflip` and `atempo`
- [x] `scraper.py` contains `BaseVideoSource`, `TikTokSource`, `DouyinSource`, `get_source` factory
- [x] Test files created in `server/tests/`
