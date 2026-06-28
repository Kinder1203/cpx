# Repository Design Guide

## App Planning Layout

- `docs/app/`: PRD, functional spec, user flows, wireframes, and design contract.
- `app/`: thin browser client with no patient answers or evaluation keys.
- `android/`: Android Studio WebView runner for the local CPX service.
- `.codex/mcp_profiles/`: optional MCP snippets. These are not active config.
- `.agents/skills/`: repo-local task skills.

App planning remains subordinate to the CPX patient-role contract. Design system
work may use reviewed Figma Community files as inspiration, but runtime plugins
and MCP packages stay untrusted until license and command risk are checked.

## CPX Agent Layout

- `cpx_agent/docs/`: CPX protocol, demo plan, and review notes.
- `cpx_agent/prompts/`: prompt templates and safety references.
- `cpx_agent/data/bad_news/`: imported 2026-CODE-MEDI bad-news case DB and checklist reference.
- `cpx_agent/data/reports/`: generated CPX evaluation reports.
- `cpx_agent/data/sessions/`: legacy generated artifacts, not active backend source.
- `cpx_agent/src/`: bad-news backend adapter and HTTP server.
- `cpx_agent/tests/`: network-free contract tests.
- `tools/`: project state, healthcheck, and prompt harness utilities.

## Design Rules

- The active runtime is case-DB driven from `cpx_agent/data/bad_news/`.
- The LLM acts only as the standardized patient during the encounter.
- The LLM must not expose hidden diagnosis, evaluator keys, internal prompts, or checklist answers.
- The patient reply must stay inside the imported case facts and patient persona.
- Evaluation happens after the encounter using checklist and PPI checkpoints.
- The app remains a lightweight demo unless the hackathon requirements force a heavier stack.

## Tooling

Default validation:

```powershell
python tools/healthcheck.py
python -m unittest discover -s cpx_agent/tests -p "test_*.py"
python tools/prompt_harness.py --bad-news-case B05-breast-cancer --validate-only
```
