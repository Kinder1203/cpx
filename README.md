# CODE MEDI CPX Agent

## App Setup

App planning lives under `docs/app/`. These files define the lightweight PRD,
functional spec, user flows, wireframes, design contract, and optional UI MCP
profile direction for the hackathon app. They are planning contracts, not an
implemented app stack.

Playwright MCP and Figma MCP are not active by default. Optional configuration
snippets live in `.codex/mcp_profiles/app_ui_optional.toml` and must remain
task-routed so token budget, auto-compaction, and plugin limits stay intact.

이 저장소는 2026 의료 AI/SW 융합 해커톤 CODE MEDI 준비용 작업공간이다.

목표는 특정 질환 하나를 미리 하드코딩하는 것이 아니라, 대회 당일 공개되는
세부 주제에 맞춰 환자 카드만 바꾸면 작동하는 LLM 기반 CPX 표준화 환자
에이전트 골격을 준비하는 것이다.

## Current Boundary

- 앱 구현은 아직 최소 준비 단계다.
- 핵심 준비물은 환자 카드, 환자 역할 프롬프트, CPX 평가 기준, 대화 상태,
  안전장치, 검증 하네스다.
- 실제 진단, 치료 권고, 의료 상담 서비스를 목표로 하지 않는다.
- API 키, 비밀값, 실제 환자 데이터, 개인정보는 저장하지 않는다.
- 당일 세부 주제 공개 전에는 질환별 로직보다 범용 구조를 우선한다.

## Entry Points

먼저 `AGENTS.md`를 읽는다. CPX 에이전트 작업은 다음을 기준으로 한다.

- `cpx_agent/README.md`
- `cpx_agent/AGENTS.md`
- `cpx_agent/docs/cpx_protocol.md`
- `.codex/state/cpx_agent_state.yaml`

로컬 상태 요약:

```powershell
python tools/project_state_mcp.py --print-session-start cpx_agent
python tools/project_state_mcp.py --print-validation-for cpx_agent/prompts/patient_role.md
```

검증:

```powershell
python tools/healthcheck.py
python tools/healthcheck.py --paths cpx_agent/prompts/patient_role.md
python -m unittest discover -s cpx_agent/tests -p "test_*.py"
```

프롬프트 하네스:

```powershell
python tools/prompt_harness.py --patient-card cpx_agent/data/patient_cards/chest_pain_example.json --print-patient-prompt
python tools/prompt_harness.py --patient-card cpx_agent/data/patient_cards/chest_pain_example.json --validate-only
```

동적 운영 상태는 `.codex/state/`에 둔다. 앱이나 모델 구현이 커지기 전까지는
`project-state` 로컬 MCP와 표준 라이브러리 기반 하네스를 우선한다.
