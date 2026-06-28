# App Documentation

This folder keeps the product and UI contract for the CODE MEDI CPX demo. It is
planning documentation, not a separate runtime source of truth.

## Reading Order

1. `prd.md`
2. `functional_spec.md`
3. `user_flows.md`
4. `wireframes.md`
5. `design.md`
6. `serious_simulation_direction.md`
7. `frontend_stack_decision.md`
8. `pixel_asset_pipeline.md`
9. `visual_quality_bar.md`

The higher-level CPX safety and role contract is
`cpx_agent/docs/cpx_protocol.md`.

## Current Contract

- The learner enters one free-text doctor utterance at a time.
- The Python service owns case selection, session state, patient replies,
  evaluation, and report generation.
- Patient replies are generated from the imported 2026-CODE-MEDI bad-news case
  database and patient-role LLM prompt contract.
- Encounter completion triggers checklist/PPI checkpoint scoring and a formative
  report.
- The browser client and Android WebView use the same local Python service.
- Live patient replies and scoring require `OPENAI_API_KEY`; Codex CLI runtime
  model calls are not part of the app.

## Deferred

Mission Map, structured question cards, patient Stability/Trust/Risk gauges,
physical-exam flows, and automatic case authoring are not part of the active
demo contract. Add them only if they directly support the confirmed bad-news
delivery station.

Playwright is for UI verification after implementation changes. Figma is used
only when a concrete source file or design reference is selected.
