---
name: diagnose-failure
description: Use when the CPX agent, prompt harness, tests, or app demo behaves incorrectly and the task is to find root cause before patching symptoms.
---

# Diagnose Failure

Start with reproduction and source-of-truth alignment.

1. Run the smallest failing command.
2. Read `AGENTS.md`, the relevant `cpx_agent/AGENTS.md`, and validation route.
3. Separate structural causes from surface symptoms.
4. Check whether failure is in patient card, prompt, state tracking, evaluator,
   app wiring, or LLM provider behavior.
5. Patch the narrowest source-of-truth layer.

Common failure classes:

- hidden diagnosis leaked
- agent switched to doctor role
- patient-card facts were fabricated
- evaluator gave real treatment advice
- app state lost earlier disclosed facts
- prompt template changed but tests/state did not

Return reproduction, root cause, changed files, validation, and residual risk.
