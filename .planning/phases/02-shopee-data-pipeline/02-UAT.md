---
status: partial
phase: 02-shopee-data-pipeline
source: [02-01-SUMMARY.md, 02-02-SUMMARY.md]
started: 2026-03-29T00:58:00+07:00
updated: 2026-03-29T01:46:00+07:00
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Start the FastAPI application from scratch (`fastapi dev server/main.py`). Server boots without errors and DB tables are created (or ready). The `/api/v1/health` endpoint returns live data indicating the server is healthy.
result: pass

### 2. Trigger Search Scraper
expected: Send a POST request to `/api/v1/crawler/shopee/search` with payload `{"keyword": "áo thun nam", "count": 2}`. Server launches a headless Chromium instance, scrapes Shopee products, and returns a JSON array of products. The `image_urls` should contain string URLs (no files downloaded), and `status` should be "PENDING".
result: issue
reported: "\"detail\": \"Unexpected error: It looks like you are using Playwright Sync API inside the asyncio loop.\\nPlease use the Async API instead.\""
severity: blocker

### 3. Upload Affiliate Session
expected: Export a dummy or real Shopee Affiliate session as a JSON file and upload it via POST `/api/v1/crawler/shopee/session`. Server should accept the file, validate it as JSON, and confirm it's saved locally.
result: pass

### 4. Batch Affiliate Conversion
expected: With PENDING products existing and a valid session file uploaded, send a POST request to `/api/v1/crawler/shopee/convert`. Server should launch Playwright, automate the Shopee Affiliate portal, and update the DB records to state "CONVERTED" with valid `affiliate_url`s.
result: blocked
blocked_by: prior-phase
reason: "blocked"

## Summary

total: 4
passed: 2
issues: 1
pending: 0
skipped: 1

## Gaps

- truth: "Send a POST request to `/api/v1/crawler/shopee/search` with payload `{\"keyword\": \"áo thun nam\", \"count\": 2}`. Server launches a headless Chromium instance, scrapes Shopee products, and returns a JSON array of products. The `image_urls` should contain string URLs (no files downloaded), and `status` should be \"PENDING\"."
  status: failed
  reason: "User reported: \"detail\": \"Unexpected error: It looks like you are using Playwright Sync API inside the asyncio loop.\\nPlease use the Async API instead.\""
  severity: blocker
  test: 2
  artifacts: []
  missing: []
