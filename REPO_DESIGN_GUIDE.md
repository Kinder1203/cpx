# Repository Design Guide

## App Planning Layout

- `docs/app/`: PRD, functional spec, user flows, wireframes, and design contract.
- `app/`: thin browser client with no patient answers or evaluation keys.
- `android/`: Android Studio WebView runner for the local CPX service.
- `.codex/mcp_profiles/`: optional MCP snippets. These are not active config; copy them into active config only for a focused task.
- `.agents/skills/app-product-spec`, `.agents/skills/app-design-system`, `.agents/skills/app-ui-qa`: app setup and QA skills.

App planning remains subordinate to the CPX patient-role contract. Design system
work may use Figma Community files as reviewed inspiration or an imported source,
but third-party plugins/MCP packages are untrusted until license and command
execution risk are checked.

## Shape

활성 트랙은 `cpx_agent/` 하나다. 루트 문서는 저장소 범위와 작업 규칙을
정의하고, 트랙 문서는 CPX 환자 에이전트 계약을 정의한다. `.codex/state/`는
현재 운영 상태와 검증 라우팅을 저장한다.

## CPX Agent Layout

- `cpx_agent/docs/`: CPX 대화 계약, 데모 플랜, 발표/시연 판단 기준.
- `cpx_agent/prompts/`: 환자 역할, 평가자, 안전장치 프롬프트 템플릿.
- `cpx_agent/data/patient_cards/`: 당일 주제에 맞춰 교체 가능한 환자 카드.
- `cpx_agent/data/sessions/`: 생성 대화 로그 자리.
- `cpx_agent/data/reports/`: 문진 평가 리포트 자리.
- `cpx_agent/tests/`: 환자 카드와 프롬프트 계약의 네트워크 없는 테스트.
- `cpx_agent/src/`: 환자 카드 코어, 세션 서비스, Codex CLI 분류기, HTTP 서버.
- `tools/`: 프로젝트 상태 요약, healthcheck, 프롬프트 하네스.

## Design Rules

- 환자 카드를 소스 오브 트루스로 둔다.
- LLM은 환자 역할만 수행한다.
- 사용자가 묻지 않은 숨은 정보를 먼저 공개하지 않는다.
- 대화 상태는 공개된 정보와 질문된 항목을 기록하는 방향으로 설계한다.
- 평가 기능은 대화 후 문진 체크리스트와 누락 항목을 보여주는 데 집중한다.
- 안전장치는 교육용 시뮬레이터 경계, 진단/치료 금지, prompt injection 방어를
  포함한다.
- 당일 주제 변경은 환자 카드와 체크리스트 교체로 흡수한다.

## Tooling

기본 MCP는 read-only `project-state` 하나다. repo-local Skills는 방향 잡기,
CPX 안전 검토, prompt harness, 실패 진단, 상태 위생, 긴 문맥 체크포인트만
둔다.

## Transition

현재 목표는 해커톤 전 lightweight 세팅이다. 표준 라이브러리 Python 서비스와
얇은 HTML 클라이언트, Android WebView 래퍼를 사용한다. 당일 요구사항으로 앱
프레임워크를 바꾸더라도 환자 카드, 프롬프트, 평가 기준, 검증 하네스는 그대로
재사용되어야 한다.
