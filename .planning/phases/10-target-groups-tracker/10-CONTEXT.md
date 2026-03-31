# Phase 10: Target Groups Tracker - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Cấu trúc tự động cào bài viết nhạy theo Groups và UI quản lý mồi. This phase delivers a mechanism to define target Facebook groups, scrape high-engagement or keyword-relevant posts, and an admin UI to review these posts before they become targets for automated comments.

</domain>

<decisions>
## Implementation Decisions

### Target Definition
- **D-01:** Target groups must be **linked to Keywords/Products**. The scraper should look for posts matching specific keywords in these groups so they are relevant to Shopee products.

### Scraping Criteria
- **D-02:** Scrape posts based on **Keyword match OR High Engagement** (e.g., > X comments/reactions). This ensures we capture both targeted topics and trending content.

### UI Presentation
- **D-03:** View scraped posts in a **Table View** (Consistent with the Products page to handle dense data effectively).

### Approval Workflow
- **D-04:** **Manual Review** required. Posts are saved as "pending" and the Admin must click "Approve" before the auto-commenting seeding job can run on them.

### the agent's Discretion
- Logic for determining "high engagement" thresholds (e.g., configurable vs hardcoded initial values).
- The exact table columns (e.g., author, content preview, reaction count, link to original fb post).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project & Roadmap
- `.planning/ROADMAP.md` — Phase 10 goals and criteria.
- `.planning/REQUIREMENTS.md` — TARG-01, TARG-02, TARG-03 requirement specifications.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Table` component from `shadcn/ui` used in `Products.tsx`.
- StatusBadge pattern from Phase 9.

### Established Patterns
- Tiered scraping (API/Playwright) from Phase 4. Using Playwright for unauthenticated/authenticated scraping depending on current FB limits.

### Integration Points
- Add `Target Groups` and `Scraped Posts` tabs/menus in the Dashboard UI.
- New domain `app/domains/target_groups/` for the backend logic, similar to `shopee_crawler`.

</code_context>

<specifics>
## Specific Ideas

- Followed recommendations provided during discussion.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
