---
name: pre-implementation-grill
description: Use before major CODE MEDI CPX agent implementation, app-framework selection, prompt-contract changes, MCP/skill/tooling changes, or demo-structure changes to align intent before editing.
---

# Pre-Implementation Grill

Use this skill before substantial work where misunderstanding intent would
create scope drift or burn hackathon time.

## Required Reads

1. `AGENTS.md`
2. `README.md`
3. `REPO_DESIGN_GUIDE.md`
4. `cpx_agent/README.md`
5. `cpx_agent/AGENTS.md`
6. `cpx_agent/docs/cpx_protocol.md`
7. `.codex/state/cpx_agent_state.yaml`
8. Target folder docs when the target path is known

## Alignment Checklist

- User intent
- Smallest useful work slice
- Public interface or data contract
- Likely touched files
- Assumptions Codex must not invent
- Explicit non-goals
- Acceptance checks
- Demo-time risk

Keep real patient data, API keys, hidden diagnosis disclosure, diagnosis or
treatment advice, and unnecessary framework/plugin expansion out of scope unless
the user explicitly requests that phase.

## Output

1. `Confirmed intent`
2. `Constraints`
3. `Out of scope`
4. `Implementation-ready summary`
5. `Remaining uncertainty`
