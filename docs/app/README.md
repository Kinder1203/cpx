# App Setup Index

이 폴더는 CODE MEDI CPX 앱을 당일 빠르게 만들기 위한 제품/디자인/검증 세팅이다.
현재 단계에서는 실제 프레임워크, API 제공자, 배포 환경을 고정하지 않는다.

## Reading Order

1. `docs/app/prd.md`
2. `docs/app/functional_spec.md`
3. `docs/app/user_flows.md`
4. `docs/app/wireframes.md`
5. `docs/app/design.md`
6. `docs/app/serious_simulation_direction.md`
7. `docs/app/frontend_stack_decision.md`
8. `docs/app/pixel_asset_pipeline.md`
9. `docs/app/design_reference_intake.md`
10. `docs/app/visual_quality_bar.md`

CPX 환자 역할, 환자 카드, 프롬프트, 평가 계약은 여전히
`cpx_agent/docs/cpx_protocol.md`가 상위 source of truth다.

## App Setup Stance

- The app direction is a 2D pixel CPX serious simulation, not a plain chat UI.
  `serious_simulation_direction.md` records the stage loop, encounter composition,
  patient state semantics, and safe game-like wording.
- `frontend_stack_decision.md` records React + Vite + TypeScript as the default app
  implementation path while keeping `app_framework_decided: false` until a scaffold exists.
- `pixel_asset_pipeline.md` records the sprite-sheet and metadata contract for pixel art
  assets without requiring final assets before the hackathon.
- 앱은 CPX 표준화 환자 시뮬레이터를 조작하고 시연하기 위한 얇은 UI다.
- UI는 환자 역할 LLM, 평가기, 안전 프롬프트를 바꾸는 source of truth가 아니다.
- 당일 주제 공개 전에는 무거운 design system, remote MCP, 배포 스택을 기본값으로
  켜지 않는다.
- Playwright/Figma MCP는 기본 비활성이다. 앱 구현 또는 디자인 소스가 생긴 뒤
  `.codex/mcp_profiles/app_ui_optional.toml`에서 필요한 블록만 검토해서 켠다.

## External Research Snapshot

- Microsoft Playwright MCP README는 코딩 에이전트에는 CLI+Skills가 더 토큰
  효율적이고, MCP는 지속 브라우저 상태와 긴 탐색 루프에 유리하다고 설명한다:
  https://github.com/microsoft/playwright-mcp
- Figma 공식 MCP 문서는 remote server가 `https://mcp.figma.com/mcp`를 쓰며,
  Codex가 desktop/remote/write-to-canvas/skills를 지원하는 클라이언트로 listed되어
  있다고 설명한다: https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server
- Figma community-resources는 agent skills와 개발 리소스를 모으지만 Figma가
  endorsement하지 않으며 보안 검토가 필요하다고 명시한다:
  https://github.com/figma/community-resources
- MCP reference servers README도 reference implementation은 production-ready가
  아니므로 threat model과 safeguards를 직접 검토하라고 경고한다:
  https://github.com/modelcontextprotocol/servers

## Repo-Local App Skills

- `app-product-spec`: PRD, 기능명세서, 유저플로우, 와이어프레임을 CPX 계약에 맞춰
  좁히는 skill.
- `app-design-system`: `design.md`, Figma 파일, 디자인 토큰, 컴포넌트 규칙을
  정리하는 skill.
- `app-ui-qa`: 앱 구현 후 Playwright CLI, in-app browser, 선택 MCP를 골라 UI
  검증 루프를 구성하는 skill.
