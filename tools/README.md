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
python tools/prompt_harness.py --bad-news-case B05-breast-cancer --validate-only
python tools/prompt_harness.py --bad-news-case B05-breast-cancer --print-patient-prompt
python tools/prompt_harness.py --bad-news-case B05-breast-cancer --print-checklist-prompt
```

## Bootstrap

```powershell
python tools/bootstrap_codex.py
```

Use this to check project-scoped Codex config, local MCP config, skills, and
core state files without starting app work.
