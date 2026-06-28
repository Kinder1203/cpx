# App Documentation

이 폴더는 현재 구현된 CODE MEDI CPX 앱의 제품·화면 계약을 관리한다.
아이디어 백로그와 현재 계약을 섞지 않는다.

## Reading Order

1. `prd.md`
2. `functional_spec.md`
3. `user_flows.md`
4. `wireframes.md`
5. `design.md`
6. `serious_simulation_direction.md`
7. `frontend_stack_decision.md`
8. `pixel_asset_pipeline.md`
9. `visual_quality_bar.md`

환자 역할, 정보 공개, 평가 안전 계약의 상위 source of truth는
`cpx_agent/docs/cpx_protocol.md`다.

## Current Contract

- 학습자 입력은 자유 문장 질문 하나다.
- 질문은 서버에서 환자 카드의 문진 개념으로 정규화한다.
- 환자 답변은 스키마 및 실행 모드 검사를 통과한 카드에 있는 내용만 반환한다.
- 문진 뒤 학습자가 문제 요약, 우선 진단, 감별 진단, 판단 근거를 제출한다.
- 현재 평가는 카드에 정의된 문진·임상 판단 규칙을 결정적으로 적용한다.
- 약점 프로필은 실행 모드에서 허용된 카드 라이브러리의 다음 케이스 선택에만 사용한다.
- 브라우저 클라이언트와 Android WebView는 같은 Python 서비스를 사용한다.

## Deferred

Mission Map, 질문 카드, Patient Stability/Trust/Risk, 신체진찰, 자동 환자 생성은
현재 기능 계약이 아니다. 외부 근거 링크는 카드에 직접 연결된 관련 자료가 있을 때만
해당 피드백에 표시한다.

Playwright는 구현 후 UI 검증에 사용한다. Figma는 구체적인 디자인 소스가 정해졌을
때만 사용한다.
