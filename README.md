# CODE MEDI CPX Agent

This repository is the CODE MEDI hackathon workspace for a CPX educational
simulation. The active track is `cpx_agent/`.

## App Setup

App planning lives under `docs/app/`. The functional vertical slice lives in
`app/`, its Python service lives in `cpx_agent/src/`, and the Android Studio
runner lives in `android/`. The Android project remains a WebView runner around
the local service.

Playwright MCP and Figma MCP are not active by default. Optional configuration
snippets live in `.codex/mcp_profiles/app_ui_optional.toml`.

## Current Boundary

- Confirmed topic: bad-news delivery.
- Active backend basis: copied 2026-CODE-MEDI bad-news case DB, patient-role LLM
  prompt contract, checklist evaluator, and PPI evaluator.
- Runtime server: `cpx_agent/src/cpx_server.py` using
  `cpx_agent/src/bad_news_backend.py`.
- Runtime data: `cpx_agent/data/bad_news/`.
- Generated reports: `cpx_agent/data/reports/bad_news/`.
- Live patient replies and scoring require `OPENAI_API_KEY`.
- Codex CLI model calls are not part of the app runtime.
- Real patient data, private student data, API keys, and secrets must not be
  stored in the repo.

The original source folder
`C:\Users\user\Desktop\2026-CODE-MEDI\backend` is read-only for this project.

## Entry Points

Read `AGENTS.md` first. For CPX agent work, use:

- `cpx_agent/README.md`
- `cpx_agent/AGENTS.md`
- `cpx_agent/docs/cpx_protocol.md`
- `.codex/state/cpx_agent_state.yaml`

Local state summary:

```powershell
python tools/project_state_mcp.py --print-session-start cpx_agent
python tools/project_state_mcp.py --print-validation-for cpx_agent/src/bad_news_backend.py
```

Validation:

```powershell
python tools/healthcheck.py
python -m unittest discover -s cpx_agent/tests -p "test_*.py"
```

Run the local service:

```powershell
python -m cpx_agent.src.cpx_server --port 8787
```

Browser: `http://127.0.0.1:8787`

Android emulator: `http://10.0.2.2:8787`
