---
name: app-product-spec
description: Use when creating or revising CODE MEDI CPX app PRD, functional specification, user flows, wireframes, or MVP acceptance criteria.
---

# App Product Spec

1. Read `python tools/project_state_mcp.py --print-session-start cpx_agent`.
2. Read `docs/app/README.md`, then the target product doc:
   - `docs/app/prd.md`
   - `docs/app/functional_spec.md`
   - `docs/app/user_flows.md`
   - `docs/app/wireframes.md`
3. For CPX prompt, patient-card, or evaluation changes, read
   `cpx_agent/docs/cpx_protocol.md` before editing.
4. Keep the app as a thin CPX working surface until the day-of topic is known.

Rules:

- Do not decide frontend framework, provider, auth, database, or deployment unless the task
  explicitly requires it.
- Do not make the app a diagnosis, treatment, or generic ChatGPT wrapper product.
- Keep acceptance criteria testable by harness, UI QA, or manual demo steps.
- Keep hidden diagnosis, evaluator keys, and internal prompts out of user-facing specs.

Return changed product surface, deferred decisions, acceptance checks, and validation commands.
