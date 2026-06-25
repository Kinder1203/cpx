---
name: state-hygiene
description: Use when editing .codex/state files in the CODE MEDI CPX agent project to keep active CPX state, validation routing, MCP policy, and recent decisions compact and non-duplicative.
---

# State Hygiene

Required reads:

1. `AGENTS.md`
2. `README.md`
3. `REPO_DESIGN_GUIDE.md`
4. `.codex/state/global_state.yaml`
5. `.codex/state/validation_map.yaml`
6. the touched state file
7. the source-of-truth doc that corresponds to that state file

Placement rules:

- Durable folder roles and guardrails belong in `README.md` / `AGENTS.md`.
- Active CPX stance belongs in `.codex/state/cpx_agent_state.yaml`.
- Tool admission belongs in `.codex/state/mcp_policy.yaml`.
- Artifact interpretation belongs in `.codex/state/artifact_policy.yaml`.
- Recent pivots belong in `.codex/state/recent_decisions.md`.
- Do not use dynamic state as a session transcript or patient-card store.

Validation:

```powershell
python tools/healthcheck.py
python tools/project_state_mcp.py --print-track-summary cpx_agent
python tools/project_state_mcp.py --print-validation-for .codex/state/cpx_agent_state.yaml
```
