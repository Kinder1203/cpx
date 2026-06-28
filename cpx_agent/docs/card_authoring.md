# Patient Card Authoring and Review

## 목적과 한계

환자 카드는 에이전트가 즉석에서 임상 사실을 만드는 대신, 승인된 범위 안에서만 환자를
연기하도록 하는 실행 계약이다. “객관적으로 100% 맞는 자동 생성”은 보장할 수 없다.
가이드라인도 개별 합성 환자의 이름·정확한 시각·수치까지 검증하지 않으므로, 근거가
지지하는 임상 구조와 교육 목적으로 만든 합성 세부 정보를 명시적으로 분리한다.

## 고정 섹션

모든 카드는 `schema_version=1.2.0`과 다음 최상위 섹션을 가져야 한다.

- `publication`: `draft | demo_only | validated | retired`, 합성 교육 콘텐츠 표시, 임상 검토 상태
- `evaluation_metadata`: `formative`, rubric 버전, `not_validated`
- `evidence`: 합성 필드, 원문 출처, 출처별 지원 대상
- `curriculum_metadata`: 계통, 빈도, 임상 중요도
- `patient_profile`: 환자가 일관되게 기억할 고정 사실과 비공개 진단
- `disclosure_policy`, `conversation_style`, `cpx_checklist`
- `clinical_assessment_rubric`, `adaptive_curriculum`, `safety_notes`

각 `cpx_checklist.<id>`와 `clinical_assessment_rubric.<id>`는 적어도 하나의 근거 출처
`supports`에 포함되어야 한다. URL은 HTTPS 원문 또는 DOI를 사용한다. 검색 결과 페이지,
LLM 답변, MCP/skill/plugin 이름은 근거로 기록하지 않는다.

`conversation_style.opening_line`은 임상 사실을 포함하지 않는 짧은 인사말로 작성한다.
주호소를 포함한 체크리스트 정보는 학습자가 질문한 뒤에만 공개한다. 감별 진단 평가는
단순 입력 개수가 아니라 `term_group_match`의 서로 다른 진단군을 기준으로 하며, 동일
진단의 한글·영문 별칭은 하나의 진단군에 함께 둔다.

## 근거 우선순위

1. 최신 전문학회 임상진료지침 또는 공공기관 지침
2. 지침이 없을 때 체계적 문헌고찰·합의문
3. 교육 표현을 보완할 때 검토 가능한 표준 교과 자료

출처의 적용 범위를 `scope`에 제한적으로 쓴다. 예를 들어 “흉통 병력 청취 영역을
지지하지만 합성 환자의 정확한 발병 시각은 검증하지 않는다”라고 기록한다. 출처 간
충돌, 오래된 근거, 특정 집단에만 적용되는 권고는 카드 게시 전 해결하거나 명시한다.

## 작성·검토·게시 절차

1. 빈도와 임상 중요도를 근거로 교육 목표를 선택한다. 약점 데이터만으로 질환을 정하지 않는다.
2. 원문을 확보하고 체크리스트·rubric 지원 대상을 매핑한다.
3. 합성 환자 사실과 제한 공개 응답을 작성하고 `draft`로 저장한다.
4. prompt harness, 단위 테스트, 누설·일관성 검사를 실행한다.
5. 임상의가 임상 사실, 표현, 위험 신호, 평가 기준, 출처 적용 범위를 검토한다.
6. 수정 요청을 반영한 뒤 승인자 식별자와 검토·재검토 날짜를 기록하고 `validated`로 바꾼다.
7. 근거 또는 rubric 변경 시 버전을 올리고 다시 검토한다. 폐기 카드는 `retired`로 바꾼다.

`production` 실행 모드는 `validated`이면서 `clinical_review.status=approved`인 카드만
읽는다. 현재 저장소의 흉통·복통 카드는 형식과 동작을 보여주는 `demo_only` 사례다.

## 향후 후보 생성

LLM은 오프라인에서 초안 후보를 만들 수 있지만 런타임에 자동 게시하지 않는다. 후보는
계약 검사를 통과한 카드 형식을 복제하고, 흔한 사례와 놓치면 위해가 큰 사례의 균형을 맞춘다.
근거 매핑, 자동 계약 검사, 임상의 승인을 모두 통과한 뒤에만 카드 라이브러리에 들어간다.
Graphify, LLM wiki, Obsidian은 카드 수와 편집 협업이 실제 병목이 된 뒤 검토한다.
