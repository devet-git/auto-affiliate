# Phase 09: Product Management - Context

**Gathered:** 2026-03-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Crawl sản phẩm Shopee background và Màn hình hiển thị danh sách SP.
This phase delivers a background crawler for scraping Shopee products based on admin criteria, and a web admin screen to manage these scraped products.

</domain>

<decisions>
## Implementation Decisions

### Criteria & Source
- **D-01:** Target scraping by **Keywords and Shop URLs** to ensure the highest relevance of products pulled into the system.

### Duplicate Handling
- **D-02:** **Skip existing products entirely**. If a scraped product already exists in the database, do not update details or log a revision.

### Scraping Frequency
- **D-03:** Run the cron job **daily** by default, but the frequency/trigger must be **configurable via the Web UI**.

### UI Presentation
- **D-04:** Use a **data-heavy Table view** optimized for administration and filtering, containing small product image thumbnails.

### the agent's Discretion
- Database Schema: How to store the configuration for crawler frequency (e.g., Settings table vs. hardcoded env vars initially overridden by UI config).
- Scraper approach: Using Playwright vs API calls for Shopee depending on current rate limits and bot protections.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project & Roadmap
- `.planning/ROADMAP.md` — Phase 9 goals and criteria.
- `.planning/REQUIREMENTS.md` — PROD-01, PROD-02 requirement specifications.

</canonical_refs>
