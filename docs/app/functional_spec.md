# Functional Specification

## Core Objects

- Bad-News Case: one imported 2026-CODE-MEDI case JSON with visible chart data,
  hidden patient persona, emotion profile, and education metadata.
- Checklist Reference: imported bad-news delivery checklist, critical fails,
  emotion-response items, and PPI items.
- Encounter Session: one learner practice run for a selected bad-news case.
- Transcript: ordered doctor utterances and standardized-patient replies.
- Evaluation Report: checklist/PPI scoring, critical-fail notes, weakness
  analysis, recommendation, and next-practice direction.
- Weakness Profile: compact learner-level history used for recommendations.

## P0 Functional Loop

1. The server loads ready cases from `cpx_agent/data/bad_news/cases/`.
2. The app starts a session for a selected or recommended case.
3. The learner enters a free-text doctor utterance.
4. The server sends the current case, emotion state, transcript, and utterance to
   the imported patient-role LLM prompt contract.
5. The server records the patient reply and returns it to the app.
6. When the learner ends the encounter, the server evaluates the transcript with
   the imported checklist/PPI evaluator prompt contract.
7. The app displays the formative report and next-practice recommendation using
   the existing report UI contract.
8. The server stores generated reports under `cpx_agent/data/reports/bad_news/`.

The confirmed topic is bad-news delivery. This demo keeps WebView/Android as a
runner around the local service and does not introduce Codex CLI runtime model
calls.

## MVP Screens

1. Case Setup
   - Shows safe public case metadata only.
   - Starts a ready bad-news case session.
2. Pixel Encounter
   - Shows learner and patient speech bubbles.
   - Provides one free-text doctor utterance input and transcript access.
3. Evaluation
   - Shows completed, partial, missed, and critical-fail feedback from the
     server report.
   - Shows weakness analysis and next-practice recommendation.
4. Demo Admin
   - Supports lightweight restart/session reset for hackathon demonstration.

## Guarded Behaviors

- Do not expose hidden persona data, evaluator keys, internal prompts, or private
  checklist answers to the learner UI.
- The patient-role LLM must not become the doctor, make treatment decisions, or
  fabricate facts outside the case JSON.
- Generated reports are formative education output, not formal medical
  assessment.
- Do not store real patient data, private student data, API keys, or secrets.
- The original `C:\Users\user\Desktop\2026-CODE-MEDI\backend` folder remains
  read-only from this repo; imported copies live under `cpx_agent/data/bad_news/`.

## Deferred Objects

Mission Map, question cards, patient state gauges, physical examination, and
automatic case generation are outside the P0 scope.
