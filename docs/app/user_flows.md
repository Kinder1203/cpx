# User Flows

## Flow 1: Prepare Case

1. 참가자가 환자 카드를 선택하거나 붙여넣는다.
2. 앱이 required sections와 leak-sensitive fields를 검증한다.
3. 앱은 safe metadata만 보여준다.
4. 검증 실패 시 어떤 섹션이 빠졌는지만 보여주고 내부 정답은 노출하지 않는다.

## Flow 2: Run Encounter

1. 학생 사용자가 문진을 시작한다.
2. 환자 에이전트는 환자 역할로만 답한다.
3. 학생이 추가 질문을 하면 환자 카드에 있는 범위에서만 답한다.
4. 학생이 세션 종료를 누른다.

## Flow 3: Evaluate

1. 앱이 transcript를 evaluator prompt에 전달한다.
2. 평가기는 checklist coverage와 missed items를 계산한다.
3. 앱은 교육용 피드백과 안전 경고를 보여준다.
4. 내부 평가 키와 숨겨진 진단명은 표시하지 않는다.

## Flow 3A: Run Pixel CPX Mission

1. The learner enters a mission from the stage map.
2. The case brief shows safe metadata, chief complaint, and objective.
3. The pixel encounter opens with the patient in the upper-left and learner back-view in the
   lower-right.
4. The learner selects structured question cards or uses optional free input.
5. The patient answers only from the patient card and conversation state.
6. Patient Stability, Trust, and Risk update after clinically meaningful actions.
7. The learner submits the Decision Board.
8. The CPX report explains missed items, safety issues, communication gaps, and the next
   mission recommendation.

## Flow 4: Day-of Case Swap

1. 당일 주제 공개 후 새 환자 카드 초안을 만든다.
2. `tools/prompt_harness.py --validate-only`로 검증한다.
3. 앱은 기존 UI/flow를 유지하고 카드만 교체한다.
4. 데모 전 최소 한 번 encounter + evaluation dry run을 수행한다.
