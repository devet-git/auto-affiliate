---
wave: 3
depends_on: [09-PLAN-01-schema-and-api-PLAN.md, 09-PLAN-02-shopee-crawler-PLAN.md]
files_modified:
  - web/package.json
  - web/src/pages/products/index.tsx
  - web/src/components/CrawlerConfigCard.tsx
  - web/src/components/CrawlerSourcesTable.tsx
  - web/src/routes.tsx
autonomous: false
requirements_addressed:
  - PROD-01
---

# Plan 03: Frontend Product Management UI

<objective>
To build the Web Dashboard interface for managing Shopee products, adjusting crawler settings, and defining crawler keywords/shop URLs.
</objective>

<tasks>

<task>
<description>
Create Data Table component for Shopee Products
</description>
<read_first>
- web/src/pages/products/index.tsx
</read_first>
<action>
1. Generate `web/src/pages/products/index.tsx`.
2. Use Shadcn UI DataTable components to display the fetched product data (`/api/v1/shopee/products`).
3. Columns must include: Thumbnail (first image in `image_urls`), `title`, `price`, `status`, `keyword`.
4. Ensure pagination works if returning a large dataset.
5. Create an API hook `useShopeeProducts` or similar utilizing React Query.
</action>
<acceptance_criteria>
- `web/src/pages/products/index.tsx` exists and uses Shadcn `Table`.
- Defines columns `Thumbnail`, `title`, `price`.
</acceptance_criteria>
</task>

<task>
<description>
Create Crawler Config & Sources UI
</description>
<read_first>
- web/src/components/CrawlerConfigCard.tsx
</read_first>
<action>
1. Generate a component or section on the Products Page to edit Global Crawler Config (`frequency_hours`). Hook up to `PATCH /api/v1/shopee/config`.
2. Generate an inline list/table to add and toggle `CrawlerSource`s (Keywords/URLs).
   - "Add new Keyword" input.
   - List existing active and inactive keywords with a toggle "Active/Inactive".
   - Hook up to POST & DELETE `/api/v1/shopee/sources`.
</action>
<acceptance_criteria>
- `web/src/components/CrawlerConfigCard.tsx` contains API calls to update frequency.
- The UI contains inputs for new Keywords and URLs.
</acceptance_criteria>
</task>

<task>
<description>
Update Sidebar/Routes
</description>
<read_first>
- web/src/routes.tsx
- web/src/components/AppSidebar.tsx
</read_first>
<action>
1. Add `/products` route pointing to the new `ProductsPage`.
2. Add a navigation item in `AppSidebar` or equivalent layout sidebar to link to `/products`, showing "Products" and an appropriate icon (e.g., `Package`).
</action>
<acceptance_criteria>
- `web/src/routes.tsx` or similar router file has a path `/products`.
</acceptance_criteria>
</task>

</tasks>

<verification>
1. Run `npm run dev` in `web/`.
2. Navigate to `http://localhost:5173/products` (or equivalent).
3. The page loads without crashing, and config settings can be updated and saved.
</verification>
