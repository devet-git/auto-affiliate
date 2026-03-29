# Phase 6: Tooling & Setup - Verification & Validation

**Phase:** 6
**Date:** 2026-03-29

## Strategy Overview
Verify `start-all.bat` correctly spawns 5 separate command windows with specifically named titles and delays between backend execution.
Verify `stop-all.bat` successfully targets processes with these exact Window titles.

## Architecture Checks

### 1. `start-all.bat` structure
- **Component**: Start script
- **Action**: Read `start-all.bat` contents
- **Success Pattern**: Contains 5 `start cmd /k "title ..."` lines.

### 2. `stop-all.bat` structure
- **Component**: Stop script
- **Action**: Read `stop-all.bat` contents
- **Success Pattern**: Contains `taskkill /FI "WINDOWTITLE eq ..."` lines.
