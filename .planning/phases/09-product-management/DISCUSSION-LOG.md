# Phase 09 - Discussion Log

**Date:** 2026-03-30

## Area: Criteria & Source for scraping
**Question:** What triggers the crawler? By search keywords, specific category URLs, or shop URLs? (Recommended: Keywords and Shop URLs for highest relevance)
**User Response:** Như đề xuất của bạn (Keywords and Shop URLs)

## Area: Duplicate handling & Updates
**Question:** When the crawler finds a product that already exists in our DB, do we update the details (price/stock), skip it entirely, or log it as a revision?
**User Response:** skip (Skip entirely)

## Area: Scraping Frequency
**Question:** How often should the backend background job run? (e.g., Daily, every 12 hours, weekly?)
**User Response:** mặc định là daily, nhưng cho phép tôi tùy chỉnh trên giao diện

## Area: UI Presentation
**Question:** For PROD-01, should the web interface use an image-heavy Grid view (like an e-commerce catalog) or a data-heavy Table view (better for admin sorting/filtering)? (Recommended: Table view with small thumbnails for admin efficiency)
**User Response:** Như đề xuất (Table view with small thumbnails)
