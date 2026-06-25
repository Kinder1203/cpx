---
name: cpx-guard
description: Use after code, prompt, docs, state, skills, MCP, or tooling changes in the CODE MEDI CPX agent project to prevent patient-role, medical-safety, and source-of-truth drift.
---

# CPX Guard

Read `AGENTS.md`, `.codex/state/validation_map.yaml`, the touched folder rules,
and the corresponding source-of-truth docs.

For each touched path:

1. choose the longest matching validation-map rule
2. deduplicate commands and docs to reopen
3. verify patient role, prompt, state, and tests agree
4. verify no hidden diagnosis or internal evaluation leak was introduced
5. report residual risks

Pressure points:

- `cpx_agent/docs/cpx_protocol.md`
- `cpx_agent/prompts/patient_role.md`
- `cpx_agent/prompts/evaluator.md`
- `cpx_agent/prompts/safety.md`
- `.codex/state/cpx_agent_state.yaml`
- `tools/healthcheck.py`
- `tools/project_state_mcp.py`

Reject drift toward diagnosis/treatment advice, real patient data storage,
patient-card fact fabrication, hidden diagnosis disclosure, or unnecessary
tooling.

Minimum validation:

```powershell
python tools/healthcheck.py
python -m unittest discover -s cpx_agent/tests -p "test_*.py"
```
