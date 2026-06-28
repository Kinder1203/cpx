# Recent Decisions

## 2026-06-29 - Imported 2026-CODE-MEDI Bad-News Backend

- `C:\Users\user\Desktop\2026-CODE-MEDI\backend`는 원본 참조로만 사용하고 수정하지 않는다.
- 원본 backend의 `cases/`, `cases_archive_v1/`, `checklist_reference.json`, `checklist_reference_v1_archive.json`를 `cpx_agent/data/bad_news/`에 해시 일치 복사했다.
- 현재 로컬 서버는 `bad_news_backend.py` 어댑터로 케이스 DB, 환자 역할 LLM 발화, 체크포인트/PPI 기반 채점을 연결한다.
- 기존 WebView/Android 앱 계약은 유지하되, 라이브 환자 발화와 채점에는 `OPENAI_API_KEY`가 필요하다.

## 2026-06-29 - Bad-News Delivery Scope and Runtime Cleanup

- 세부 주제는 `나쁜 소식 전하기`로 확정되었다.
- 환자 발화 생성은 가져온 backend 프롬프트 계약 기반 LLM 어댑터가 담당한다.
- 이 저장소는 현재 WebView/로컬 API/세션 기록/대화 종료 후 체크포인트 리포트 경계를 유지한다.
- Codex CLI 기반 런타임 모델 호출과 선택적 개념 분류기는 데모 범위에서 제거한다.
- 과거 범용 CPX 산출물은 리포트 데모에 필요한 케이스·체크포인트·검증 경계만 남긴다.

## 2026-06-28 - Evidence-Gated Cards and Resumable Sessions

- Patient-card contract `1.2.0` records a neutral opening line, synthetic fields,
  item-level source coverage, publication status, clinical review status, and formative
  rubric version. Differential concepts use explicit synonym groups.
- Existing chest- and abdominal-pain cards remain `demo_only`; production mode fails
  closed until at least one clinically approved `validated` card exists.
- Sessions now persist in local SQLite and restore after a server restart. Real patient
  or private learner data remains prohibited.
- Runtime case generation, Graph/Wiki memory, and unreviewed automatic publishing remain
  excluded. Source retrieval tools may assist authoring but do not replace source records
  or clinician approval.

## 2026-06-27 - Guarded Functional Vertical Slice

- Active track is `cpx_agent/`.
- Runtime patient replies were originally schema-checked, release-eligible card text;
  the current scoped demo delegates patient utterance generation to the external team
  component.
- Clinical-assessment concept evidence is credited only when disclosed in the current
  encounter; obvious negation and duplicate differential entries do not earn credit.
- Adaptive practice selects deterministically from release-eligible cards. Automatic patient
  generation, Graph/Wiki memory, and self-training remain deferred.
- The 2D pixel serious-simulation design remains unchanged. The report only adds focus
  handling and an existing-style action to start the release-eligible recommendation.
- Adaptive practice has two deterministic modes: remediate when important gaps remain,
  otherwise broaden to a different topic. Resolved weaknesses decay, recent cases are
  deprioritized, and uncommon cards require high or critical clinical importance.
- Report findings scroll inside their own list area, while spare encounter height expands
  the existing patient scene rather than changing the visual system.
