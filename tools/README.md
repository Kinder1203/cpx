# Tools

Local helper tools for the CODE MEDI CPX Agent scaffold.

## Project State

```powershell
python tools/project_state_mcp.py --print-session-start cpx_agent
python tools/project_state_mcp.py --print-validation-for cpx_agent/prompts/patient_role.md
```

## Healthcheck

```powershell
python tools/healthcheck.py
python tools/healthcheck.py --paths cpx_agent/prompts/patient_role.md
```

## Prompt Harness

```powershell
python tools/prompt_harness.py --patient-card cpx_agent/data/patient_cards/chest_pain_example.json --validate-only
python tools/prompt_harness.py --patient-card cpx_agent/data/patient_cards/chest_pain_example.json --print-patient-prompt
```

## Bootstrap

```powershell
python tools/bootstrap_codex.py
```

Use this to check project-scoped Codex config, local MCP config, skills, and
core state files without starting app work.
