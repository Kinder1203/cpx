# Frontend Stack Decision

This document records the default implementation path for the future CODE MEDI CPX app.
It is a decision aid, not an instruction to scaffold the app before the day-of requirements
are known.

## Decision Status

- Status: default path selected, app framework not yet scaffolded.
- Default path: React + Vite + TypeScript.
- Source of truth status: subordinate to `docs/app/wireframes.md`, `docs/app/design.md`,
  and `cpx_agent/docs/cpx_protocol.md`.
- State flag: `app_framework_decided` remains `false` until code is scaffolded.

## Why This Default

The app is expected to be a client-heavy CPX serious simulation surface: pixel encounter
scene, transcript, selected or free-form questions, patient state indicators, evaluation
report, and demo-friendly mocked backend behavior.

React + Vite + TypeScript is the preferred default because it supports fast local iteration,
simple static builds, strong component ergonomics, and a thin integration layer over the CPX
harness. It avoids committing to server routing, auth, database, deployment, or framework
conventions before the hackathon topic and constraints are known.

## Stack Contract

If the app is scaffolded under this default, start with:

- React for component composition and stateful interaction.
- Vite for local dev server, HMR, and static production build.
- TypeScript for patient-card, encounter-state, report, and sprite metadata contracts.
- CSS custom properties for design tokens.
- Tailwind or utility classes only if they map to the token contract instead of replacing it.
- Lucide icons for common commands when an icon exists.
- Playwright CLI or in-app browser checks for visual QA before optional Playwright MCP.

Do not add by default:

- Next.js server features.
- Database, auth, payment, analytics, or user account systems.
- Heavy game engines.
- Runtime Figma packages or unreviewed design MCP packages.
- Real patient data handling.

## Switch Conditions

Switch from the default path only when a concrete requirement appears.

Use Next.js or another full-stack framework if:

- The demo needs server-rendered routes, route-level data loading, or deploy-native API routes.
- Auth, team sharing, persistent remote sessions, or hosted report links become core.
- The chosen deployment environment strongly favors a full-stack framework.

Use PixiJS, Phaser, or another rendering library if:

- The encounter needs many animated entities, collision-like interactions, camera movement,
  layered particle effects, or timeline-heavy game logic.
- CSS sprite animation cannot keep the pixel scene stable and performant.

Use plain HTML/CSS/JS only if:

- The demo narrows to a static prototype or single-screen exhibit where React state management
  would slow the team down.

## Implementation Shape

Preferred first scaffold:

```text
app/
  src/
    app/
      App.tsx
      routes or screens
    components/
      cpx/
      simulation/
      report/
      ui/
    data/
      demoPatientCard.ts
    styles/
      tokens.css
      global.css
    types/
      patientCard.ts
      encounter.ts
      pixelAsset.ts
```

The first implemented screen should be the CPX working surface, not a landing page.

## Acceptance Checks

Before accepting the scaffold:

- The first viewport shows the encounter surface and safe case metadata.
- Hidden diagnosis, evaluator keys, internal prompts, and raw patient-card internals are not
  rendered in UI, DOM-visible debug JSON, screenshots, downloads, or logs intended for demo.
- Desktop and mobile layouts keep the transcript, input, patient state, and main action visible
  without overlap.
- The app can run with mocked patient response and mocked evaluation data before any API key.
- UI QA has a clear path through Playwright CLI or in-app browser screenshots.

## Deferred Decisions

- Actual scaffold timing.
- Package manager.
- Deployment target.
- LLM provider and API key setup.
- Whether Tailwind is used in code.
- Whether a game rendering library is justified.
