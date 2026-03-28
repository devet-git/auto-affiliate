---
plan: 02-02
phase: 02-shopee-data-pipeline
status: complete
completed: 2026-03-29
commit: bab2fdd
---

# Plan 02-02 Summary: Module Affiliate Link Generator

## What Was Built

Playwright CMS automation for Shopee Affiliate link conversion (D-03 — "tà đạo"):

- **`affiliate.py`** — `convert_affiliate_links(urls, state_file)` loads pre-captured browser session (Playwright `storage_state` JSON), navigates to `affiliate.shopee.vn/custom_link`, pastes URLs, extracts tracking links. Session expiry detected automatically. Batches of 10 per portal submission.
- **`service.py`** (updated) — `run_batch_affiliate_conversion()` fetches up to 20 PENDING products, calls converter, updates DB: `CONVERTED` (with `affiliate_url`) or `FAILED`.
- **`config.py`** (updated) — `SHOPEE_CMS_STATE_FILE` setting added (default: `shopee_state.json`, overridable via `.env`).
- **`router.py`** (updated) — Two new endpoints:
  - `POST /api/v1/crawler/shopee/session` — Upload Playwright storage_state JSON (validates JSON before saving).
  - `POST /api/v1/crawler/shopee/convert` — Trigger batch affiliate conversion. Returns `{converted, failed, total}`.

## Key Files
- `server/app/domains/shopee_crawler/affiliate.py` — CMS Playwright engine
- `server/app/domains/shopee_crawler/service.py` — batch conversion logic
- `server/app/domains/shopee_crawler/router.py` — `/session` and `/convert` endpoints

## Decisions Honored
- D-03: Playwright CMS automation (no Official API required) ✓
- D-01: Reuses Playwright infrastructure (shared with Phase 4 Tier-2) ✓

## Self-Check: PASSED
