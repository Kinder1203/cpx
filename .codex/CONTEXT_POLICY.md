# Codex Context and Tool Policy

이 파일은 루트 `AGENTS.md`가 참조하는 자세한 라우팅 정책이다. Codex 도구,
MCP, skill, context budget, 긴 스레드 carry-over를 다룰 때만 읽는다.

## Default Bootstrap

한 번의 compact project-state view로 시작한다.

```powershell
python tools/project_state_mcp.py --print-session-start cpx_agent
```

부족할 때만 `--print-root-summary` 또는 `--print-track-summary cpx_agent`를
쓴다. 전체 상태, 전체 skill, 전체 프롬프트, 생성 로그를 자동으로 preload하지
않는다.

## Default Tool Surface

- `project-state`: 현재 범위, 상태 요약, skill index, 검증 라우팅의 첫 선택.
- `Serena`: 대상 코드 모듈이 명확할 때 symbol-aware 탐색이나 리팩터링에만 사용.
- `openaiDeveloperDocs`: OpenAI API나 Codex 관련 최신 공식 문서가 필요할 때만 사용.
- Repo-local skills: 현재 작업과 description이 맞을 때만 사용.
- Shell과 `rg`: broad dump보다 대상 경로와 bounded output을 우선한다.

## App-Installed Plugins

앱 플러그인은 기본 비활성이다. 이 프로젝트의 소스 오브 트루스는 로컬 파일,
환자 카드, 프롬프트, 하네스다.

| Plugin | Posture | Reason |
| --- | --- | --- |
| Binance | Disabled | CPX 앱 준비와 무관하고 큰 도구 표면을 추가한다. |
| OpenAI Developers | Disabled by default | API 키나 최신 API 문서가 필요한 별도 작업에서만 사용. |
| Data Analytics | Disabled | 대시보드나 분석 리포트를 요청받을 때만 사용. |
| Browser/Chrome/Computer Use | Disabled | 로컬 앱 UI 검증이 필요할 때만 별도 사용. |
| Drive/Docs/Slides/PDF | Disabled | 발표 자료나 문서 산출물 요청 시에만 사용. |

## Token and Output Budget

- 자동 주입 프로젝트 지침은 32 KiB 아래로 유지한다.
- Codex config의 `model_auto_compact_token_limit`는 80000으로 유지한다.
- Codex config의 `tool_output_token_limit`는 6000으로 유지한다.
- `.codex/state/cpx_agent_state.yaml`은 800 lines 또는 36 KiB를 넘으면
  compact 검토 대상으로 본다. 크기만으로 실패 처리하지는 않는다.
- 한 tool output은 6k tokens 이하를 목표로 한다.
- 로그, 생성 세션, 환자 카드 전체 묶음을 통째로 출력하지 않는다.
- 정책 문구는 `AGENTS.md`, docs, state 중 하나의 canonical 위치에 둔다.
- 긴 스레드는 objective, decisions, touched files, validation, blockers,
  explicit non-goals만 남기고 `context-checkpoint`로 이어간다.

## Memory

프로젝트 규칙은 체크인된 문서와 `.codex/state`에 둔다. 별도 프로젝트 memory는
만들지 않는다. 사용자 레벨 memory는 힌트로만 쓰고, 현재 파일로 검증한다.

## Tool Admission Checklist

새 도구, plugin, MCP, skill을 추가하기 전:

1. 반복적으로 해결할 정확한 gap을 말한다.
2. 기존 하네스나 `project-state`로 해결 불가능한지 확인한다.
3. startup context cost와 network/auth cost를 본다.
4. read-only, public, narrow 도구를 우선한다.
5. 왜 존재하는지와 어떻게 검증하는지 기록한다.
6. 필요가 없어지면 비활성화하거나 제거한다.
## App UI Tooling Addendum

- App planning docs live in `docs/app/` and should be opened only when the task
  touches PRD, functional spec, user flows, wireframes, design, or app UI QA.
- Playwright MCP and Figma MCP stay disabled by default. Use
  `.codex/mcp_profiles/app_ui_optional.toml` only for focused app-design or
  UI-QA work, then remove the active config again.
- Prefer Playwright CLI or the in-app browser for short UI checks. Use
  Playwright MCP only when persistent browser state or long exploratory loops
  justify the context cost.
- Prefer official Figma MCP when a specific Figma file, frame, or design-system
  library is part of the task. Treat community files as reviewed inputs, not as
  repo source of truth.
