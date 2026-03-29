# Phase 07: Design System UI - Context

**Gathered:** 2026-03-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Implementing a unified Design System via StitchMCP to apply new colors, typography, and styling tokens globally across the React Frontend App, refreshing the existing screens (Dashboard, Approval Queue, Campaigns) without functional regressions.

</domain>

<decisions>
## Implementation Decisions

### Theme Vibe & Colors
- **D-01:** Support both Light and Dark modes with a sleek, vibrant modern brand color (e.g., deep Indigo or Violet).
- **D-02:** Default the application to Dark Mode, as it serves as a technical automation control center.

### Shape & Typography
- **D-03:** Use subtle rounded corners on UI elements (e.g., Shadcn's radius scaling at ~0.5rem/8px) to balance professional and modern aesthetics.
- **D-04:** Use a clean, modern Google Font (e.g., Inter or Onest) as the default font family for superior readability on data-heavy dashboards.

### Screen Revamp Scope
- **D-05:** Scope is strictly limited to global style updates via StitchMCP and minor presentation-level Tailwind adjustments. Do not alter the core DOM structure or functionality of existing tested screens (Dashboard, Campaigns, Approval).

### the agent's Discretion
- Micro-animations, subtle background gradients, specific accent colors, and specific StitchMCP configuration options are left to the agent's aesthetic judgment to maximize the "Wow" factor while retaining peak usability.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project & Roadmap
- `.planning/ROADMAP.md` — Phase 7 details and success criteria.
- `.planning/REQUIREMENTS.md` — UI-01, UI-02 requirement specifications.

### Existing Codebase
- `web/src/index.css` — Existing Tailwind and Shadcn CSS variables.
- `web/tailwind.config.js` — Integration point for StitchMCP theme token updates.
- `web/src/App.tsx` — Root component for applying global theme providers.

</canonical_refs>
