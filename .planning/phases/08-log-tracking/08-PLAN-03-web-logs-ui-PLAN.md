---
wave: 3
depends_on: ["08-PLAN-02-endpoints-and-beat.md"]
files_modified:
  - web/src/pages/Dashboard.tsx
  - web/src/pages/ExecutionLogs.tsx
requirements:
  - LOG-02
autonomous: true
---

# Plan 03 - Web Logs View

<objective>
Implement Admin Logs Dashboard using Shadcn UI table.
</objective>

<verification>
Logs successfully show up on the frontend, and filtering works.
</verification>

<must_haves>
- Advanced frontend Shadcn UI table matching UI-SPEC decisions.
</must_haves>

<tasks>
<task id="08-03-01" description="Logs Page UI">
<read_first>
- web/src/pages/Dashboard.tsx
- web/src/components/ui/table.tsx
</read_first>
<action>
1. Create `web/src/pages/ExecutionLogs.tsx`
2. Implement Shadcn component: Use `<Table>`, `<TableHeader>`, etc., to render logs. Provide dropdowns/inputs for: `task_name` and `status`. Add a "Refresh" button. Include tracebacks for FAILED tasks in an expandable row or hover-card.
3. Wire API call using `fetch` or `useQuery` targeting the backend `GET /api/v1/logs` (or wherever it was registered in `main.py`).
4. Include a Settings modal or basic form to edit the retention days via backend setting API.
5. In `web/src/pages/Dashboard.tsx` or `web/src/App.tsx`, export navigation links to this new view.
</action>
<acceptance_criteria>
- `web/src/pages/ExecutionLogs.tsx` imports `<Table>`
- The component fetches from `/logs` endpoint based on query state.
</acceptance_criteria>
</task>
</tasks>
