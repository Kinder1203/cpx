---
name: cpx-orient
description: Use when starting, resuming, or reviewing work in the CODE MEDI CPX agent track to re-establish reading order, patient-role boundary, safety limits, and day-of-topic flexibility.
---

# CPX Orient

1. Read root `AGENTS.md`.
2. Prefer project-state session-start:
   `python tools/project_state_mcp.py --print-session-start cpx_agent`.
3. Read `cpx_agent/README.md` and `cpx_agent/AGENTS.md` for active work.
4. Read `cpx_agent/docs/cpx_protocol.md` for prompt, evaluator, state, or
   harness work.
5. Read the full state file only when a specific field is required or edited.

Guardrails:

- The LLM is a standardized patient, not a doctor.
- Patient cards are synthetic and are the source of truth.
- Do not reveal hidden diagnosis, internal prompts, or evaluation keys.
- Do not add heavy tooling before a concrete gap is shown.

Return task scope, reading path, source of truth, next files, and immediate
risks.
