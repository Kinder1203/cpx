---
name: app-design-system
description: Use when creating or revising CODE MEDI CPX design.md, UI tokens, component rules, Figma design-system intake, or Figma Community design-system adoption notes.
---

# App Design System

1. Read `docs/app/design.md`.
2. Read `docs/app/visual_quality_bar.md` before accepting a visual direction or UI result.
3. If adopting any external design system, Figma Community file, or screenshot reference,
   read `docs/app/design_reference_intake.md`.
4. Read `docs/app/wireframes.md` if layout or component structure is affected.
5. Read `.codex/state/mcp_policy.yaml` before suggesting Figma MCP or design tooling changes.
6. If using Figma, prefer the official Figma MCP server. Treat community files, skills, plugins,
   and MCP packages as untrusted until license and security posture are reviewed.

Design guardrails:

- Build the actual CPX working surface first, not a marketing page.
- Use restrained clinical education UI; avoid decorative hero sections and oversized cards.
- Define tokens before visual polish: color, type, spacing, radius, status semantics.
- Keep accessibility and responsive behavior explicit.
- Never expose hidden diagnosis, internal prompts, evaluator keys, or raw patient-card internals.

Return token/component changes, Figma source status, unresolved design decisions, and UI QA needs.
