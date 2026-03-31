# Phase 10: Target Groups Tracker - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-31
**Phase:** 10-target-groups-tracker
**Areas discussed:** Target Definition, Scraping Criteria, UI Presentation, Approval Workflow

---

## Target Definition

| Option | Description | Selected |
|--------|-------------|----------|
| Group URL/ID only | Crawl generic hot posts, then filter later | |
| Linked to Keywords/Products | RECOMMENDED - only crawl posts that match specific keywords | ✓ |
| Other | | |

**User's choice:** "Làm theo đề xuất" (Linked to Keywords/Products)
**Notes:** 

---

## Scraping Criteria

| Option | Description | Selected |
|--------|-------------|----------|
| Keyword match only | Any new post containing the keyword | |
| Keyword OR High Engagement | RECOMMENDED - Keyword match OR post has > X comments | ✓ |
| Recent Posts Only | Just pull the latest 20 posts regardless of engagement | |

**User's choice:** "Làm theo đề xuất" (Keyword OR High Engagement)
**Notes:** 

---

## UI Presentation

| Option | Description | Selected |
|--------|-------------|----------|
| Table View | RECOMMENDED - Consistent with Products page, dense data | ✓ |
| Visual Card Grid | Better for previewing Facebook media/images | |
| Other | | |

**User's choice:** "Làm theo đề xuất" (Table View)
**Notes:** 

---

## Approval Workflow

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-Approve | Automatically ready for the Celery seeding job | |
| Manual Review | RECOMMENDED - Admin must click 'Approve' to prevent spam | ✓ |
| Other | | |

**User's choice:** "Làm theo đề xuất" (Manual Review)
**Notes:** 
