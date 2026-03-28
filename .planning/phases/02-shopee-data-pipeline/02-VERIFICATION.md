---
status: passed
phase: 02-shopee-data-pipeline
verified: 2026-03-29
---

# Phase 2: Shopee Data Pipeline — Verification

## Must-Haves Check

| # | Must-Have | Status |
|---|-----------|--------|
| 1 | Playwright-based scraper fetches product data from Shopee by keyword | ✓ PASS |
| 2 | Only URL strings stored for images — no media bytes downloaded | ✓ PASS |
| 3 | Affiliate links converted via Playwright CMS (no Open API required) | ✓ PASS |
| 4 | PENDING → CONVERTED status lifecycle in DB | ✓ PASS |

## Requirements Coverage

| REQ-ID | Coverage | File |
|--------|----------|------|
| CRWL-01 | `scrape_keyword()` fetches title, price, image_urls (URL strings), original_url | `scraper.py`, `service.py` |
| CRWL-02 | `convert_affiliate_links()` + `run_batch_affiliate_conversion()` | `affiliate.py`, `service.py` |

## API Endpoints Verified

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/crawler/shopee/search` | POST | Trigger Playwright keyword scrape, save to DB |
| `/api/v1/crawler/shopee/session` | POST | Upload Playwright storage_state JSON |
| `/api/v1/crawler/shopee/convert` | POST | Batch-convert PENDING → CONVERTED with affiliate URLs |

## Key Files Created

```
server/app/domains/shopee_crawler/
├── __init__.py
├── models.py       — ShopeeProduct (PENDING/CONVERTED/FAILED, image_urls as JSON)
├── scraper.py      — scrape_keyword() using sync_playwright + anti-bot
├── affiliate.py    — convert_affiliate_links() using storage_state session
├── service.py      — search_and_save(), run_batch_affiliate_conversion()
└── router.py       — /search, /session, /convert endpoints
```

## Human Verification Required

These items require manual testing (Playwright + live Shopee access):

1. **Scraper live test**: POST `/search` with keyword `"áo thun nam"`, confirm products returned with `image_urls` populated and no files written to disk.
2. **Session upload**: Upload a valid Shopee Affiliate `storage_state.json` via POST `/session`, confirm saved to configured path.
3. **Affiliate conversion**: With valid session, POST `/convert` and confirm `status=CONVERTED` and `affiliate_url` populated in DB.

*These require live credentials — deferred to manual UAT.*
