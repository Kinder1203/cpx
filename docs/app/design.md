# Design System Setup

## Demo Priority

The demo is judged visually before the backend is inspected. Treat UI/UX quality as the
highest app-layer priority while keeping backend behavior mocked or lightweight until the
day-of requirements are known.

Use `visual_quality_bar.md` as the acceptance standard for implemented screens and
`design_reference_intake.md` before adopting any Figma Community file or external design
system.

## Design Intent

CODE MEDI CPX should feel like a focused clinical education tool, not a hospital diagnosis
product and not a marketing landing page. The UI should be calm, scannable, and reliable under
demo pressure.

The intended visual identity is a 2D pixel CPX serious simulation. Game-like presentation is
used to improve access, attention, and learning retention, while the wording and feedback stay
clinically serious.

## Visual Direction

- Use a restrained medical/education palette, not a one-note blue/cyan poster clone.
- Prefer dense but readable operational layouts over decorative hero sections.
- Show a phase label only when it helps the learner choose the next action. Internal rubric
  coverage and always-true safety invariants are not learner-facing status indicators.
- Use icons for commands where obvious: start, reset, export, send, warning, checklist.
- Keep cards shallow and purposeful: case setup, transcript, evaluation sections.
- Use pixel art for the encounter scene, not for every control. Product controls should remain
  readable, accessible, and stable.
- Treat Rhythm Doctor, Pokemon battle screens, and Duolingo-style progression as structural
  references only. Do not copy protected assets, layouts, characters, sound, or trade dress.

## Token Contract

Initial tokens to define before UI implementation:

- Color: background, surface, border, text, muted text, accent, success, warning, danger.
- Typography: body, label, panel heading, report heading.
- Spacing: 4, 8, 12, 16, 24, 32.
- Radius: default 6-8px; avoid oversized rounded cards.
- Components: button, input/chat composer, tabs, phase label, checklist row,
  transcript message, alert, modal.
- P0 simulation components: pixel encounter stage, learner/patient speech, transcript control,
  risk flag, weakness tag, next-case preview.
- Deferred components: question cards, Decision Board fields, physical-examination controls,
  and mission progression.

## Animation Contract

- Keep animations purposeful: idle breathing, speaking/typing feedback, and report transition.
- Use CSS sprite steps or small frame loops before introducing heavier animation tooling.
- Avoid animation that hides text, blocks input, or makes clinical feedback ambiguous.
- Every animated patient state must have a static fallback for screenshots and accessibility.

## Figma Direction

Figma MCP is useful only after one of these exists:

- A selected Figma frame or component library.
- A Figma Community file intentionally chosen as a design-system seed.
- A need to send a live localhost UI back into Figma for iteration.

Use the official Figma MCP remote server first when available. Community Figma files or skills
must be treated as inspiration or a reviewed dependency, not as source of truth. Before adopting
one, record:

- File URL and license/usage terms.
- Whether components support responsive app surfaces, not just landing pages.
- Token names and whether they map cleanly to code variables.
- Accessibility basics: contrast, focus states, input states.
- Any third-party plugin/MCP package involved and its security posture.

## App Design Checklist

- The first screen is the actual CPX working surface, not a hero/landing page.
- The patient role boundary is visible in wording but not over-explained.
- The UI never displays hidden diagnosis, evaluator keys, internal prompts, or raw secret state.
- Empty/loading/error states exist for patient card validation, LLM response, and evaluation.
- Desktop and mobile layouts keep input, transcript, and the current primary action reachable
  without overlap.
- Playwright or browser QA captures desktop and mobile screenshots before final demo.
