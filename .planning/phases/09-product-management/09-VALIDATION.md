# Phase 09: Product Management - Validation

## Dimension 8: Nyquist Validation Requirements

### V-01: Crawler Trigger Testing
**Given** the crawler frequency is set to Daily and a keyword source "áo thun" exists
**When** the scheduler task executes
**Then** it should queue a background job for Shopee scraping.
**Verification method**: Monitor `TaskLog` to see successful dispatch. 

### V-02: Duplicate Prevention
**Given** product A already exists in `shopee_products`
**When** the crawler encounters product A again
**Then** no new database row should be created and the old row's details remain untouched.
**Verification method**: `select count(*) from shopee_products where original_url = '...'` returns precisely 1 before and after.

### V-03: Product Data View
**Given** 10 products exist in the database
**When** the admin navigates to the Products screen
**Then** a Data Table should render 10 rows with thumbnails, price, and title.

### V-04: UI Config Persistence
**Given** the admin updates the crawler frequency in the Web UI
**When** the API receives the `PATCH /api/v1/settings/crawler`
**Then** the DB should update the `next_run` or `frequency` value correctly.
