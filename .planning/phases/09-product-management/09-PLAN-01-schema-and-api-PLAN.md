---
wave: 1
depends_on: []
files_modified:
  - server/app/domains/shopee_crawler/models.py
  - server/app/domains/shopee_crawler/router.py
  - server/app/domains/shopee_crawler/services.py
  - server/app/core/celery_app.py
autonomous: false
requirements_addressed:
  - PROD-01
  - PROD-02
---

# Plan 01: Product Management Schema & API

<objective>
To create the database infrastructure for managing crawling triggers (Keywords, Shop URLs) and crawler configuration, and expose standard CRUD APIs so the backend and frontend can interact safely.
</objective>

<tasks>

<task>
<description>
Update Database Schema with Crawler Settings
Add the `CrawlerSource` model to hold keywords and shop URLs, and a singleton `CrawlerConfig` for the frequency.
</description>
<read_first>
- server/app/domains/shopee_crawler/models.py
- .planning/phases/09-product-management/09-CONTEXT.md
</read_first>
<action>
1. In `server/app/domains/shopee_crawler/models.py`:
- Add an `enum` for `SourceType`: `KEYWORD`, `SHOP_URL`.
- Create `CrawlerSource` (table=True):
  - `id`: int
  - `source_type`: SourceType
  - `value`: str
  - `is_active`: bool default=True
- Create `CrawlerConfig` (table=True):
  - `id`: int (Primary key, usually just 1 for the singleton)
  - `frequency_hours`: int (default=24)
  - `next_run_time`: datetime (nullable)
- Create `CrawlerSourceCreate`, `CrawlerSourceUpdate`, `CrawlerConfigUpdate`, `CrawlerConfigPublic` Pydantic schemas.
- Ensure `ShopeeProduct` schema reads and Pydantic read schemas are correctly set.
</action>
<acceptance_criteria>
- `server/app/domains/shopee_crawler/models.py` contains `class CrawlerSource(SQLModel, table=True):`
- `server/app/domains/shopee_crawler/models.py` contains `class CrawlerConfig(SQLModel, table=True):`
</acceptance_criteria>
</task>

<task>
<description>
Create API Router & Services for Shopee Crawler settings and products.
</description>
<read_first>
- server/app/domains/shopee_crawler/router.py
- server/app/domains/shopee_crawler/services.py
</read_first>
<action>
1. In `server/app/domains/shopee_crawler/services.py`:
- `get_or_create_config()`: fetches `id=1` or creates one with defaults.
- `update_config()`: patches the config.
- CRUD for `CrawlerSource`.
- CRUD for `ShopeeProduct` (fetching lists with pagination/filters).

2. In `server/app/domains/shopee_crawler/router.py`:
- Expose `GET /api/v1/shopee/config`, `PATCH /api/v1/shopee/config`
- Expose `GET /api/v1/shopee/sources`, `POST /api/v1/shopee/sources`, `DELETE /api/v1/shopee/sources/{id}`
- Expose `GET /api/v1/shopee/products` to fetch products list
</action>
<acceptance_criteria>
- `server/app/domains/shopee_crawler/router.py` contains `@router.get("/config"`
- `server/app/domains/shopee_crawler/router.py` contains `@router.get("/products"`
- `server/app/domains/shopee_crawler/services.py` defines functions for CRUD operations.
</acceptance_criteria>
</task>

</tasks>

<verification>
1. Run `server\.venv\Scripts\alembic revision --autogenerate -m "Add crawler config and sources"`
2. Run `server\.venv\Scripts\alembic upgrade head`
3. Hit `GET /api/v1/shopee/config` using curl/Swagger and verify it returns a valid default object.
</verification>
