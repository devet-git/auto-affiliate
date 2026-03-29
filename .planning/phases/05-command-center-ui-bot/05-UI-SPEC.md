# UI Design Contract: Command Center
**Date:** 2026-03-29
**Framework:** React + Vite + Tailwind CSS + Shadcn UI

## 1. Visual Aesthetics
- **Theme**: Dark mode default (modern black/slate/zinc).
- **Typography**: Inter (Google Fonts).
- **Core Components**: 
  - `shadcn/ui/card`
  - `shadcn/ui/table`
  - `shadcn/ui/button`
  - `shadcn/ui/dialog` (Inline edit modals)
  - `shadcn/ui/toast` (Notifications)

## 2. Page Structure
### Login Screen (`/login`)
- **Layout**: Centered login card, solid dark background.
- **Form**: Email/Password + Submit Button.

### Command Center Layout
- **Sidebar**: Logo, Navigation links (Approval Queue, Campaigns, Settings).
- **Top Header**: User Profile / Logout, Current Theme Toggle.
- **Main Area**: Fluid width with a max-width container, padded content area.

### Approval Queue (`/dashboard/approval`)
- **Header Actions**: Toggle View Group (IconTable, IconLayoutGrid), Bulk Approve Button.
- **Table View (`view=table`)**:
  - Columns: ID, Thumbnail (avatar), Title, Source, Status, Actions.
  - Actions: Edit (IconPencil), Approve (IconCheck), Reject (IconX).
- **Grid View (`view=grid`)**:
  - Masonry or flexible CSS grid of Cards.
  - Card Header: Thumbnail/Video Preview.
  - Card Content: Inline editable `textarea` for caption, Source badge.
  - Card Footer: Approve/Reject split buttons.
- **Empty State**: Centered illustration "No videos pending approval. Relax!"

## 3. Micro-Interactions
- Clicking "Edit" opens a Shadcn Dialog.
- Valid Approval/Rejection triggers a subtle success toast and optimism UI update (removes item from list instantly).
- Toggle view animate with minimal framer-motion layout transitions.
