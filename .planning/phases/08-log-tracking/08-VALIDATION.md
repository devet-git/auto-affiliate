---
phase: 08
slug: log-tracking
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-30
---

# Phase 08 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `server/pyproject.toml` |
| **Quick run command** | `pytest server/tests/domains/logs -x` |
| **Full suite command** | `pytest server/tests/` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest server/tests/domains/logs -x`
- **After every plan wave:** Run `pytest server/tests/`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | LOG-01 | unit | `pytest server/tests/domains/logs/test_models.py` | ❌ W0 | ⬜ pending |
| 08-01-02 | 01 | 1 | LOG-01 | integration | `pytest server/tests/domains/logs/test_celery_signals.py` | ❌ W0 | ⬜ pending |
| 08-02-01 | 02 | 1 | LOG-02 | unit | `pytest server/tests/domains/logs/test_router.py` | ❌ W0 | ⬜ pending |
| 08-03-01 | 03 | 2 | LOG-02 | e2e | `npm run test --prefix web` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `server/tests/domains/logs/test_models.py` — stubs for TaskLog model testing
- [ ] `server/tests/domains/logs/test_celery_signals.py` — shared fixtures for mocking celery tasks

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Web UI Log Visualization | LOG-02 | React frontend visual element | Start vite server, navigate to `/dashboard/logs`, trigger a celery task, and assert the log appears in the Shadcn table correctly rendered |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
