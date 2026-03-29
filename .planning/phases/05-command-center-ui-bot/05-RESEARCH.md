# Phase 05: Command Center UI & Bot - Research Report
**Status:** COMPLETE

<objective>
Analyze the technical requirements for building a Command Center Dashboard using React Vite and Shadcn UI, as well as integrating a Telegram Bot using `aiogram` (v3+) via Webhooks within the existing FastAPI backend. Identify technical dependencies, risks, and integration points to properly plan Phase 5.
</objective>

## Technical Domains

### 1. React Vite & Shadcn UI Integration
**Findings**:
- **Initialization**: Vite handles rapid module reloading and is the modern standard over Create React App. `pnpm create vite@latest` with React and TypeScript.
- **Shadcn UI Setup**: `npx shadcn@latest init` configures `components.json`, Tailwind config, path aliases (`@/components`), and global CSS cleanly.
- **Dashboard Structure**: Needs routing (e.g., `react-router-dom`), state management for Approval Queue lists (`zustand` or React Query), and an API client (`axios`) to interact with FastAPI.
- **Component Needs**: Data Table (with toggleable Grid/Card views), Modals/Dialogs for Inline Edit of captions, Forms for Campaign creation.

### 2. Telegram Bot Integration (Aiogram 3 Webhooks)
**Findings**:
- **Framework**: `aiogram` v3+ provides native async capabilities and robust webhook handling.
- **Webhook vs Long Polling**: Since the backend is already a FastAPI web server running persistently, Webhooks are far superior. When Telegram receives a message (e.g., `/approve <id>`), it POSTs to our FastAPI `/webhook` endpoint.
- **Validation**: Requires setting `WEBHOOK_SECRET` via `X-Telegram-Bot-Api-Secret-Token` header to ensure requests are securely originating from Telegram.
- **API Setup**: The backend needs an endpoint (e.g., `/api/telegram/webhook`) that receives the `aiogram.types.Update` payload. `aiogram` provides `SimpleRequestHandler` (for aiohttp) but for FastAPI, we can map `await dp.feed_update(bot, update)`.
- **Outbound Notifications**: We can simply inject `bot.send_message(chat_id, text)` into our Celery jobs when a video requires approval.

## Validation Architecture

**(Dimension 8 applies here):**
- **Test Strategy**: Start local Vite dev server. Verify Shadcn CLI works. Mock the `/telegram/webhook` endpoint with a dummy POST request containing an expected secret to verify security gates. Test that changing the UI view from Table to Grid doesn't lose state.

## Conclusion
The architecture is solid:
- Frontend: `Vite` + `React` + `Shadcn UI` + `Tailwind` + `Zustand/React Query`.
- Bot: `aiogram` v3 mounted onto `FastAPI` instance via webhook. Outbound messages orchestrated inside Celery tasks using singleton Bot sessions.
