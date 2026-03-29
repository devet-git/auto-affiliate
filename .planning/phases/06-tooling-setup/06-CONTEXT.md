# Phase 6: Tooling & Setup - Context

**Gathered:** 2026-03-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Gom gọn hạ tầng chạy, Setup script Start-all. Viết `.bat` (Windows) để khởi động toàn bộ dependencies bằng một click: FastAPI, tất cả các hàng đợi Celery workers, Appium Server, Vite React dev server.

</domain>

<decisions>
## Implementation Decisions

### the agent's Discretion
User deferred to the agent's recommended choices for the optimal developer experience:
- **Window Management:** Use `start` with `cmd /k` to launch each service in its own visible terminal window rather than merged logs. 
- **Startup Sequence:** Staggered starts. Introduce brief pauses (`timeout /t 5`) between operations to ensure backend dependencies (DB, Redis, Appium) are fully online before spawning Celery workers or FastAPI.
- **Process Cleanup:** Provide a companion `stop-all.bat` script that uses `taskkill` (Node, Python, Appium, CMD sub-windows) to safely purge all background tools simultaneously, eliminating manual window hunting.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

No external specs — requirements fully captured in decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None specifically. Foundation tooling script.

### Established Patterns
- All backend execution happens inside `server/` with the `.venv` activated.
- Frontend execution runs via `npm run dev` in `web/`.

### Integration Points
- `start-all.bat` and `stop-all.bat` will reside at the project root `E:\Projects\Personal\auto-affiliate\`.

</code_context>

<specifics>
## Specific Ideas

- Set explicitly distinct titles for each popped window using `title [Service Name]` (e.g., `title FastAPI`) so that `stop-all.bat` can target those exact windows.
- Automatically activate `server\.venv` at the head of every backend sub-process.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 06-tooling-setup*
*Context gathered: 2026-03-29*
