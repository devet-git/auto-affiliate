---
wave: 1
depends_on: []
files_modified:
  - web/index.html
  - web/src/index.css
  - web/tailwind.config.js
  - web/src/pages/Dashboard.tsx
  - web/src/pages/ApprovalQueue.tsx
  - web/src/pages/Campaigns.tsx
autonomous: true
requirements_addressed:
  - UI-01
  - UI-02
---

# Objective
Implement the new Design System via StitchMCP and CSS variables with an Indigo/Violet brand color, dark mode default, and apply minor presentation updates to the main screens without altering core functional DOM structure.

## Tasks

<task>
  <action>
    Configure StitchMCP Project & Design System.
    1. Run `mcp_StitchMCP_create_project` to get a project ID.
    2. Run `mcp_StitchMCP_create_design_system` to set tokens (Vibrant Indigo/Violet primary color, dark mode background, 8px rounding, Geist/Inter typography).
    3. Update `web/src/index.css` mapping the decided tokens to CSS variables:
    `--primary` -> deep violet/indigo in oklch
    `--radius: 0.5rem;`
    Update `.dark` root values accordingly. Setup dark mode as default if possible or ensure it looks best.
  </action>
  <read_first>
    - web/src/index.css
    - web/tailwind.config.js
  </read_first>
  <acceptance_criteria>
    - `web/src/index.css` contains updated `--primary` and `--radius: 0.5rem;` values.
  </acceptance_criteria>
</task>

<task>
  <action>
    Integrate Typography.
    Add Google Fonts `<link>` for `Geist` or `Inter` to `web/index.html`.
    Update `web/tailwind.config.js` `theme.fontFamily.sans` to prioritize the new font.
    Update `web/src/index.css` var `--font-sans` if necessary.
  </action>
  <read_first>
    - web/index.html
    - web/tailwind.config.js
  </read_first>
  <acceptance_criteria>
    - `web/index.html` contains googleapis link for the font.
    - `web/tailwind.config.js` or `index.css` references the new font family as default.
  </acceptance_criteria>
</task>

<task>
  <action>
    Refresh Main Screens styling.
    Open `web/src/pages/Dashboard.tsx`, `web/src/pages/ApprovalQueue.tsx`, `web/src/pages/Campaigns.tsx`.
    Add Tailwind presentation classes to conform to the new aesthetics:
    - Add subtle background gradients (`bg-gradient-to-br`) or enhanced spacing if appropriate.
    - Ensure card layouts use the new rounded corners and proper padding.
    - Do NOT alter DOM logic or functionality.
  </action>
  <read_first>
    - web/src/pages/Dashboard.tsx
    - web/src/pages/ApprovalQueue.tsx
    - web/src/pages/Campaigns.tsx
  </read_first>
  <acceptance_criteria>
    - The specified page files are modified.
    - No logical functions or existing hooks are completely removed.
  </acceptance_criteria>
</task>

## Verification
- Change directory to `web/` and run `npm run build` to ensure no syntax errors.
- Ensure the primary colors in `web/src/index.css` are updated to match the design system.

## Must Haves
- Dark mode / default styling matches the Indigo/Violet theme.
- UI-01 and UI-02 are fully covered.
