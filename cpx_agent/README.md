# CPX Agent Track

이 트랙은 CODE MEDI 해커톤의 핵심 산출물인 LLM 기반 CPX 표준화 환자
에이전트를 준비한다.

## Product Idea

사용자는 의대생 또는 평가자다. LLM은 의사가 아니라 환자 역할을 수행한다.
환자 카드는 숨겨진 병력, 증상, 감정 상태, 공개 정책, 체크리스트를 담고,
LLM은 질문받은 범위 안에서만 일관되게 답한다.

대화 종료 후에는 문진 체크리스트와 누락 항목을 평가해 교육용 피드백을 만든다.

## Minimum Demo Flow

1. 당일 세부 주제를 환자 카드 JSON으로 정리한다.
2. 환자 역할 프롬프트에 환자 카드를 주입한다.
3. 사용자가 문진 질문을 입력한다.
4. 에이전트는 환자처럼 답하되 진단명과 내부 정보를 누설하지 않는다.
5. 대화 로그를 저장한다.
6. 평가 프롬프트 또는 규칙 기반 체크리스트로 문진 누락 항목을 보여준다.

## Current Files

- `docs/cpx_protocol.md`: 환자 역할, 상태, 평가, 안전 계약.
- `docs/demo_plan.md`: 해커톤 당일 시연 플랜.
- `prompts/patient_role.md`: 환자 역할 프롬프트 템플릿.
- `prompts/evaluator.md`: 문진 평가 프롬프트 템플릿.
- `prompts/safety.md`: 안전장치 프롬프트 템플릿.
- `data/patient_cards/chest_pain_example.json`: synthetic 예시 환자 카드.
- `tests/`: 네트워크 없는 계약 테스트.

## Validation

```powershell
python tools/healthcheck.py
python -m unittest discover -s cpx_agent/tests -p "test_*.py"
python tools/prompt_harness.py --patient-card cpx_agent/data/patient_cards/chest_pain_example.json --validate-only
```
