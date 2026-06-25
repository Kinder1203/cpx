---
name: app-ui-qa
description: Use after CODE MEDI CPX app UI implementation or visual changes to choose Playwright CLI, in-app browser, screenshots, or optional Playwright MCP validation.
---

# App UI QA

1. Read `docs/app/wireframes.md`, `docs/app/design.md`, and
   `docs/app/visual_quality_bar.md`.
2. Read `.codex/mcp_profiles/README.md` before enabling any optional browser MCP.
3. Prefer local dev server plus Playwright CLI or in-app browser checks for routine QA.
4. Use Playwright MCP only when persistent page state, accessibility-tree introspection, or
   long-running exploratory loops justify the token cost.

Minimum QA once an app exists:

- Desktop screenshot.
- Mobile screenshot.
- Nonblank main surface.
- Chat input usable and not overlapping transcript.
- Case setup, encounter, and evaluation states visible or reachable.
- Safety/hidden fields not rendered in DOM-visible debug views.
- Console and network errors reviewed when a dev server is running.
- Visual pass against the anti-AI UI checklist.

Return tested URLs/viewports, screenshots or observations, failures, and remaining risk.
