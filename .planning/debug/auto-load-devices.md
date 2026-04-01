---
status: resolved
issue: auto-load-devices
started: 2026-03-31T23:18:00Z
updated: 2026-03-31T23:18:00Z
---

# Debug Session: auto-load-devices

## 1. Symptoms
- **Reported Issue:** "Không thể tải danh sách thiết bị" (Cannot load device list).
- **Feature Request:** Automatically load connected devices, toggle active status on the UI, avoid manual addition but allow editing the name/description.
- **Expected:** The `ping_devices` task automatically registers new devices. Missing columns (`missed_pings`, `is_active`) on the `Device` model shouldn't crash SQLite.

## 2. Hypotheses
1. The API `GET /devices` is crashing because `missed_pings` was added to `Device` model but the SQLite `auto_affiliate.db` schema was not migrated.
2. We need an `is_active` field in `Device` so the UI can toggle participation.
3. The `ping_devices` task can automatically insert newly discovered ADB udids into the SQLite DB so manual `POST /devices` is not strictly necessary.

## 3. Evidence
- User confirmed `/devices` API failure.
- SQLite does not auto-migrate new fields gracefully by default with `SQLModel.metadata.create_all`.

## 4. Root Cause
- Missing database migration for new columns.
- Missing auto-registration logic in the `ping_devices` Celery background worker.

## 5. Next Actions
- [ ] Inject `missed_pings` and `is_active` into SQLite via script.
- [ ] Add `is_active: bool = Field(default=True)` to `Device`.
- [ ] Update `ping_devices` to conditionally `session.add(new_device)` if an `adb` udid isn't in DB.
- [ ] Send human-verify check to confirm API resolves.
