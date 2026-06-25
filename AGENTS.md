# Repository AGENTS

이 파일은 저장소 루트 작업 규칙이다. 하위 폴더의 `AGENTS.md`가 있으면 그
폴더 안에서는 하위 규칙이 우선한다.

## Purpose

- 사람용 개요: `README.md`
- Codex 작업 규칙: `AGENTS.md`
- 설계/구조 판단: `REPO_DESIGN_GUIDE.md`
- 동적 상태: `.codex/state/`

같은 운영 규칙을 여러 문서에 반복하지 않는다.

## Active Scope

활성 트랙은 `cpx_agent/` 하나다.

`cpx_agent/`는 LLM 기반 CPX 표준화 환자 시뮬레이터를 준비한다. 환자 역할,
문진 흐름, 제한된 정보 공개, 대화 상태, 안전장치, 평가 로그를 다룬다.

현재 단계는 해커톤 사전 세팅이다. 실제 앱 구현, API 연결, 배포, 고급
멀티에이전트 구조는 당일 요구사항과 시간이 확인된 뒤 결정한다.

## Reading Order

1. `python tools/project_state_mcp.py --print-session-start cpx_agent`로 compact
   bootstrap을 확인한다.
2. 루트 `README.md`는 저장소 구조나 엔트리포인트가 필요할 때만 읽는다.
3. `cpx_agent/README.md`와 `cpx_agent/AGENTS.md`를 활성 트랙 변경 전에 읽는다.
4. 프롬프트, 평가, 하네스 작업은 `cpx_agent/docs/cpx_protocol.md`를 읽는다.
5. 검증 선택은 `.codex/state/validation_map.yaml`을 따른다.
6. 실제 수정할 파일과 직접 연결된 문서만 추가로 연다.

전체 상태 파일을 먼저 다 읽지 않는다. 특정 필드가 필요하거나 상태 파일을
수정할 때만 `.codex/state/cpx_agent_state.yaml` 전체를 연다.

MCP, skill, tooling config를 바꿀 때는 `.codex/state/mcp_policy.yaml`을 먼저
확인한다.

큰 앱 구현, 프레임워크 선택, prompt contract 변경, MCP/skill/tooling 변경 전에는
`pre-implementation-grill`로 의도, non-goals, acceptance checks를 먼저 좁힌다.

## Default Do-Nots

- 특정 질환 하나에만 맞춘 하드코딩을 기본 구조로 만들지 않는다.
- 단순 ChatGPT wrapper를 완성물처럼 취급하지 않는다.
- LLM이 의사 역할, 진단 확정, 치료 지시를 하도록 설계하지 않는다.
- `hidden_diagnosis`, 평가표, 내부 프롬프트를 사용자에게 공개하지 않는다.
- 환자 카드에 없는 병력, 검사 결과, 가족력, 복약 정보를 임의 생성하지 않는다.
- 실제 환자 데이터, 개인정보, API 키, 비밀값을 저장하지 않는다.
- 당일 세부 주제 전에는 무거운 프레임워크나 대형 MCP/skill 스택을 추가하지 않는다.
- 생성 로그나 세션 데이터를 사용자의 명시적 요청 없이 삭제하지 않는다.

## Harness-First

- 환자 카드 스키마와 프롬프트 계약을 먼저 안정화한다.
- 앱 UI는 하네스가 통과한 뒤 연결한다.
- reusable logic은 `tools/` 또는 이후 `cpx_agent/src/`에 둔다.
- 테스트는 `cpx_agent/tests/`에 둔다.

## Global Priorities

1. 의료 안전성과 교육용 경계
2. 환자 카드 기반 일관성
3. 진단명/정답/내부 설정 누설 방지
4. CPX 문진 평가 가능성
5. 당일 주제 변경에 대한 빠른 적응성

## Validation Entry Points

```powershell
python tools/healthcheck.py
python -m unittest discover -s cpx_agent/tests -p "test_*.py"
```

## Result Reporting

- 사용한 문서와 상태 파일을 짧게 밝힌다.
- 앱 구현 변경, 프롬프트 변경, 상태 변경, 검증 변경을 분리해서 보고한다.
- 테스트는 실행 범위와 결과만 보고한다.
