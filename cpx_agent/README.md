# CPX Agent Track

이 트랙은 CODE MEDI 해커톤의 핵심 산출물인 LLM 기반 CPX 표준화 환자
에이전트를 준비한다.

## Product Idea

사용자는 의대생 또는 평가자다. LLM은 의사가 아니라 환자 역할을 수행한다.
환자 카드는 숨겨진 병력, 증상, 감정 상태, 공개 정책, 체크리스트를 담고,
런타임은 질문받은 범위 안에서 스키마 검증을 통과한 카드 답변만 일관되게 반환한다.

문진 뒤 학습자가 임상 판단을 제출하면 문진 체크리스트와 카드 정의 rubric을 각각
평가해 교육용 피드백을 만든다.

## Minimum Demo Flow

1. 당일 세부 주제를 환자 카드 JSON으로 정리한다.
2. 런타임이 환자 카드의 참조 무결성과 공개 금지 항목을 검증한다.
3. 사용자가 자유 문장으로 문진 질문을 입력한다.
4. 로컬 규칙 또는 선택적 Codex CLI 분류기가 질문을 환자 카드 개념에 매핑한다.
5. 서비스는 스키마 검증과 실행 모드의 게시 상태 검사를 통과한 환자 카드 답변만 공개한다.
6. 대화 상태와 이벤트는 로컬 SQLite에, 약점 프로필은 로컬 JSON에 저장한다.
7. 학습자가 문제 요약, 우선 진단, 감별 진단, 판단 근거를 제출한다.
8. 카드 정의 규칙으로 문진 누락과 임상 판단을 구분해 보여준다.
9. 보완이 필요하면 약점 관련 카드를, 수행이 충분하면 다른 계통의 임상 유용성이 높은
   실행 모드에서 허용된 카드를 다음 연습으로 연결한다.

프롬프트와 skills/harness는 카드·계약을 개발 시점에 검증하는 방어선이다. 현재
런타임의 안전 경계는 카드 검증, 제한 공개 상태, 결정적 평가가 담당하며 Codex CLI는
환자 답변을 만들지 않고 개념 ID만 낮은 추론 수준으로 분류한다. 분류기 실패 시에는
로컬 키워드 매칭과 카드 고정 fallback 응답만 사용한다. CLI에는 짧은 시간 제한,
결과 캐시, 연속 실패 회로 차단기가 적용된다.

현재 포함된 두 카드는 `demo_only` 합성 교육 사례이며 임상의 검토가 완료되지 않았다.
`--release-mode production`은 `validated`와 임상 승인 상태를 모두 충족한 카드가 없으면
서버 시작을 거부한다. 평가는 rubric 버전이 표시되는 형성평가이며 정식 평가 도구가 아니다.

## Current Files

- `docs/cpx_protocol.md`: 환자 역할, 상태, 평가, 안전 계약.
- `docs/card_authoring.md`: 근거 추적, 임상 검토, 게시 상태를 포함한 카드 작성 절차.
- `docs/demo_plan.md`: 해커톤 당일 시연 플랜.
- `prompts/patient_role.md`: 환자 역할 프롬프트 템플릿.
- `prompts/evaluator.md`: 문진 평가 프롬프트 템플릿.
- `prompts/safety.md`: 안전장치 프롬프트 템플릿.
- `data/patient_cards/`: 흉통·복통 synthetic 예시 환자 카드.
- `src/cpx_core.py`: 카드 검증, 제한 공개, 평가, 적응형 루프 코어.
- `src/codex_patient.py`: 자유 질문을 카드 개념으로만 분류하는 Codex CLI 어댑터.
- `src/cpx_service.py`, `src/cpx_server.py`: 세션 서비스와 동일 출처 HTTP API.
- `../app/`: 환자 답변과 평가 기준을 포함하지 않는 브라우저 클라이언트.
- `../android/`: Android Studio WebView 실행 래퍼.
- `tests/`: 네트워크 없는 계약 테스트.

## Validation

```powershell
python tools/healthcheck.py
python -m unittest discover -s cpx_agent/tests -p "test_*.py"
python tools/prompt_harness.py --patient-card cpx_agent/data/patient_cards/chest_pain_example.json --validate-only
```

## Run

```powershell
python -m cpx_agent.src.cpx_server --port 8787 --llm codex
```

임상 승인 카드만 허용하려면 `--release-mode production`을 추가한다.

브라우저는 `http://127.0.0.1:8787`, Android Emulator는 `android/` 프로젝트에서
`http://10.0.2.2:8787`을 사용한다.
