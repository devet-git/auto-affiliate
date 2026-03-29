---
phase: 03
slug: content-sourcing-social-seeding
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-29
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `pyproject.toml` or `pytest.ini` |
| **Quick run command** | `pytest tests/test_shopee_crawler.py` |
| **Full suite command** | `pytest tests/` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/` (for unit testing logic)
- **After every plan wave:** Run `pytest tests/` and manually verify a downloaded video via CLI runner.
- **Before `/gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | SEED-01 | unit | `pytest tests/test_scraper.py` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | SEED-02 | manual | `python -m appium_test` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_scraper.py` — stubs for SEED-01
- [ ] `tests/test_ffmpeg.py` — stubs for Deduplication
- [ ] `pytest` installed and available

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| FB Appium Login/Comment | SEED-02 | Requires real physical Android device to overcome Checkpoint. | Connect phone via USB, launch Appium Server, run Python stub file that comments on a target ID. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
