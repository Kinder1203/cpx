# Hackathon Demo Plan

## Active Topic

The confirmed station is bad-news delivery. The demo starts a case from the
imported 2026-CODE-MEDI bad-news DB, lets the learner type doctor utterances,
uses an LLM to role-play the patient, and scores the completed transcript with
the imported checklist/PPI checkpoints.

## Demo Script

- Problem: bad-news delivery is hard to practice consistently with only static scripts.
- Solution: a standardized-patient simulation backed by curated case data and checkpoint scoring.
- Differentiator: this is not a generic chatbot; patient replies stay inside the case persona, and the final report is checklist/PPI based.
- Demo: start a bad-news case, ask free-text questions or deliver the result, finish the encounter, then review missed items and next-practice direction.

## Minimum UI

- Existing 2D pixel encounter scene.
- Free-text doctor utterance input.
- Transcript and completion action.
- Educational report with checklist results, feedback, weakness summary, and next case.

## Boundaries

- Do not expose hidden diagnosis, checklist keys, internal prompts, or evaluator output in the UI.
- Do not use the retired chest-pain or abdominal-pain synthetic cards as runtime cases.
- Do not require Codex CLI model calls for the demo.
