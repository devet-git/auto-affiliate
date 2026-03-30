# Phase 08: Log Tracking - Context

**Gathered:** 2026-03-30
**Status:** Ready for planning

<domain>
## Phase Boundary

System execution logging and admin visibility. This phase delivers a database table for Celery task logs, an admin UI to trace executions with filtering, and an automated background cleanup job.

*Out of Scope:* Real-time log streaming via WebSockets.
</domain>

<decisions>
## Implementation Decisions

### Log Granularity
- **D-01:** Log everything (Started, Succeeded, Failed, Retried). Gives perfect history auditability for Celery tasks.

### Data Structure
- **D-02:** Store full Python tracebacks for errors, plus a JSON column for task arguments (args/kwargs) to make debugging trivial from the UI.

### Dashboard UI
- **D-03:** Build an advanced table with filters (by task name, status success/fail) and date range.

### Retention Policy
- **D-04:** Auto-delete old logs via a daily Celery Beat job to prevent DB bloat.
- **D-05:** The retention period (e.g., 7 or 30 days) must be user-configurable, rather than hardcoded.

### the agent's Discretion
- Database layer: Exact SQLAlchemy/SQLModel schema field names and indexing strategy.
- Frontend layer: Choice of React components (e.g., Shadcn Table vs Data Table) to implement the advanced filtering.
- Settings storage: How to store the configurable retention period (e.g., Environment Variable `.env` vs Database Settings table) is left up to the implementation phase, provided it is easily modifiable by the admin.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Requirements
- `.planning/ROADMAP.md` — Phase 8 goals and criteria
- `.planning/REQUIREMENTS.md` — LOG-01, LOG-02 specifications

### Relevant Codebase Patterns
- `server/app/core/celery_app.py` — Celery configuration to hook into for task transitions.
</canonical_refs>
