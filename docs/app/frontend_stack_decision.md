# Frontend Stack Decision

This document records the implementation path for the CODE MEDI CPX functional vertical slice.

## Decision Status

- Status: minimal functional slice implemented.
- Default path: plain HTML/CSS/JavaScript client, Python standard-library service, and Android WebView runner.
- Source of truth status: subordinate to `docs/app/wireframes.md`, `docs/app/design.md`,
  and `cpx_agent/docs/cpx_protocol.md`.
- State flag: `app_framework_decided` is `true` for the current vertical slice.

## Why This Default

The current app is a focused CPX serious simulation surface: pixel encounter scene,
free-form questions, transcript, evaluation report, and the imported bad-news local service.

Plain browser code is sufficient for the current single-screen flow and keeps the patient
case DB, patient-role LLM call, evaluation, and report generation on the Python service. Android Studio runs
the same client in a WebView instead of duplicating domain logic in the app.

## Stack Contract

The implemented stack uses:

- HTML/CSS/JavaScript for the thin client.
- Python standard library for the session API and static serving.
- Java WebView for the Android Studio runner.
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

Keep plain HTML/CSS/JS while:

- The app remains a focused encounter and report flow without complex client routing.

## Implementation Shape

Current implementation:

```text
app/
  index.html
  app.js
  styles.css
cpx_agent/src/
  bad_news_backend.py
  cpx_server.py
android/
  app/
```

The first implemented screen should be the CPX working surface, not a landing page.

## Acceptance Checks

Before accepting the scaffold:

- The first viewport shows the encounter surface and safe case metadata.
- Hidden diagnosis, evaluator keys, internal prompts, and raw case internals are not
  rendered in UI, DOM-visible debug JSON, screenshots, downloads, or logs intended for demo.
- Desktop and mobile layouts keep the transcript, input, and main action visible
  without overlap.
- The app can run without Codex CLI runtime model calls.
- UI QA has a clear path through Playwright CLI or in-app browser screenshots.

## Deferred Decisions

- Deployment target.
- Hosted LLM provider and credential setup.
- Whether Tailwind is used in code.
- Whether a game rendering library is justified.
