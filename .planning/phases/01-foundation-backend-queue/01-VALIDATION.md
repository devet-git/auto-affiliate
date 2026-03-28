---
phase: 1
slug: foundation-backend-queue
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-28
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `pytest tests/` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | CORE-01 | unit | `pytest tests/test_health.py` | ❌ W0 | ⬜ pending |
| 1-02-01 | 02 | 1 | CORE-03 | unit | `pytest tests/test_auth.py` | ❌ W0 | ⬜ pending |
| 1-03-01 | 03 | 2 | CORE-02 | e2e | `pytest tests/test_celery.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pytest`, `httpx` (for FastAPI test client)
- [ ] `tests/test_health.py` — stubs for CORE-01
- [ ] `tests/test_auth.py` — stubs for CORE-03
- [ ] `tests/test_celery.py` — stubs for CORE-02

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Swagger Docs Load | CORE-01 | Visual Check | Mở browser go tới `/docs`, test endpoint UI |
| Celery Console Log | CORE-02 | Queue Worker | Chạy worker local, push task từ code, xem log worker |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
