---
plan: 02-03
phase: 02-shopee-data-pipeline
gap_closure: true
status: complete
completed: 2026-03-29
---

# Plan 02-03: Fix Playwright Async Loop Clash — SUMMARY

## What Was Built

Converted two Playwright-calling router endpoints from `async def` to `def`:
- `trigger_shopee_search` (POST /crawler/shopee/search)
- `trigger_affiliate_conversion` (POST /crawler/shopee/convert)

FastAPI automatically offloads synchronous `def` endpoint functions to a threadpool executor, keeping them off the main asyncio event loop. `sync_playwright` requires its own event loop and crashes with `"Playwright Sync API inside the asyncio loop"` when called from within an already-running async context. The `upload_shopee_session` endpoint was intentionally left `async def` because it uses `await file.read()` and does not call Playwright.

## Key Files

### Modified
- `server/app/domains/shopee_crawler/router.py` — two endpoints converted from `async def` to `def`

## Verification

AST parse confirms:
- `def trigger_shopee_search` ✓
- `async def upload_shopee_session` ✓ (unchanged)
- `def trigger_affiliate_conversion` ✓

## Commits

- `6aedeb6` — fix(02-03): convert Playwright endpoints to sync def to avoid asyncio loop clash

## Self-Check: PASSED

All acceptance criteria met. Playwright sync API can now run in threadpool without asyncio event loop collision.
