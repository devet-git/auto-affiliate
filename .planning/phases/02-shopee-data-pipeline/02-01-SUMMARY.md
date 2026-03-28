---
plan: 02-01
phase: 02-shopee-data-pipeline
status: complete
completed: 2026-03-29
commit: 2c28bf4
---

# Plan 02-01 Summary: Module Shopee Scraper

## What Was Built

Domain `shopee_crawler` with full Playwright-based scraping pipeline:

- **`models.py`** — `ShopeeProduct` SQLModel table with `original_url`, `affiliate_url`, `title`, `price`, `image_urls` (JSON array of URL strings), `status` (PENDING/CONVERTED/FAILED), `keyword`.
- **`scraper.py`** — `scrape_keyword()` using `sync_playwright` + headless Chromium. Anti-bot measures: custom User-Agent, navigator.webdriver masking, Vietnamese locale, multi-scroll lazy-load trigger, multi-selector fallback strategy for Shopee DOM changes.
- **`service.py`** — `search_and_save()` maps raw scraper dicts to ORM objects (status=PENDING, image_urls as URL strings only per D-02). `get_pending_products()` for Wave 2 affiliate converter.
- **`router.py`** — `POST /api/v1/crawler/shopee/search` with keyword + count payload, admin JWT auth, input validation.
- **`main.py`** — Router + models registered; DB table auto-created on startup via SQLModel metadata.
- **`requirements.txt`** — `playwright>=1.40.0` added; installed + `playwright install chromium` run in venv.

## Key Files
- `server/app/domains/shopee_crawler/scraper.py` — core engine
- `server/app/domains/shopee_crawler/models.py` — DB schema
- `server/app/domains/shopee_crawler/router.py` — API endpoint

## Decisions Honored
- D-01: Playwright for anti-bot scraping ✓
- D-02: Only URL strings stored, no media downloads ✓
- D-04: Keyword/category-based input trigger ✓

## Self-Check: PASSED
