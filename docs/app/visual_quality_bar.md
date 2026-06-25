# Visual Quality Bar

This is the minimum visual standard for the CODE MEDI CPX app. The goal is a credible
hackathon demo that looks intentionally designed, not an AI-generated generic dashboard.

## Priority

- UI/UX quality is higher priority than backend completeness for the demo.
- Backend can stay mocked or lightweight if the visible CPX flow is coherent.
- The first screen must be the working CPX session surface, not a landing page.
- Visual polish must not weaken patient-role boundaries, hidden-field safety, or
  evaluation integrity.

## Anti-AI Rules

- Do not use generic AI/medical hero sections, floating gradient blobs, bokeh backgrounds,
  glass panels, neon glow, or stock-looking doctor/brain/network imagery as the main UI.
- Do not make the interface a set of oversized rounded cards with marketing copy.
- Do not rely on a single blue/cyan palette because the poster is blue. Use a restrained
  clinical base with purposeful accents for state and priority.
- Do not show decorative charts unless they answer a real CPX workflow question.
- Do not expose hidden diagnosis, evaluator keys, raw prompt text, or patient-card internals
  as debug UI.

## Screen Standard

Desktop should show:

- Case setup/status and required-field readiness.
- Encounter transcript with patient/student distinction.
- Input controls that remain reachable.
- Safety or policy state without exposing internal content.
- Evaluation/report access after the encounter.

Mobile should show:

- A compact session header with safe metadata only.
- Transcript-first flow.
- Persistent or immediately reachable input.
- Case setup and evaluation reachable through tabs, sheets, or stacked sections.
- No overlap between keyboard/input, transcript, and action controls.

## Component Standard

- Buttons use clear commands or familiar icons with labels/tooltips where needed.
- Inputs have visible labels, validation, disabled/loading states, and clear recovery paths.
- Tabs, segmented controls, and sheets are used for mode changes instead of decorative cards.
- Tables and checklists are scan-friendly, with stable row height and clear status markers.
- Empty, loading, error, and completed states are designed before the demo script is finalized.

## Token Standard

- Typography: restrained hierarchy, no viewport-scaled type, no negative letter spacing.
- Spacing: dense but not cramped; repeated surfaces use consistent gaps.
- Radius: default 8px or less unless a chosen design system requires otherwise.
- Elevation: subtle and functional; avoid stacked card shadows.
- Color: clinical neutral base, one primary action color, semantic colors for safety and
  evaluation states, and enough contrast for projector/demo viewing.

## QA Checklist

Before accepting a UI implementation or major visual change:

- Capture desktop and mobile screenshots.
- Check for text overflow, clipped controls, and incoherent overlap.
- Confirm the first viewport communicates CPX session purpose without explanatory marketing.
- Confirm input remains usable in the main encounter flow.
- Confirm loading, empty, error, disabled, and completed states are not raw browser defaults.
- Scan the palette for one-note blue/cyan or generic purple gradient drift.
- Verify no hidden/internal CPX fields are visible in labels, debug panels, DOM-visible JSON,
  screenshots, downloads, or logs intended for presentation.

## Figma Intake

- Use `docs/app/design_reference_intake.md` before adopting any Figma Community file.
- Use official Figma MCP only after a specific file is chosen and optional MCP activation is
  justified by the task.
- Imported visual systems are references; product structure remains governed by
  `docs/app/wireframes.md`.
