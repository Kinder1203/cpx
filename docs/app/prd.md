# PRD

## Product

The intended app shape is a 2D pixel CPX serious simulation. It uses game-like
accessibility, staged missions, patient state feedback, and a final CPX report to improve
history-taking, red-flag recognition, communication, and clinical reasoning.

CODE MEDI CPX 앱은 해커톤 당일 공개되는 의료 CPX 주제에 맞춰, 학생 또는 심사자가
LLM 기반 표준화 환자와 문진하고 문진 결과를 교육용으로 평가할 수 있게 하는 데모
앱이다.

## Problem

The risk is not only technical implementation. The app must avoid looking like either a
plain chatbot or a trivialized medical game. The product needs a serious-simulation frame:
approachable, visual, and game-like, but still governed by CPX patient-card and evaluation
contracts.

- 당일 주제가 바뀔 수 있어 질환별 하드코딩은 위험하다.
- 단순 ChatGPT wrapper는 CPX 평가 가능성, 정보 공개 제한, 안전 경계를 보여주기
  어렵다.
- 의료 맥락에서는 진단/치료 조언, 내부 정답 누설, 실제 환자 데이터 저장을
  방지해야 한다.

## Target Users

- 참가자: 환자 카드, 문진 세션, 평가 로그를 빠르게 확인하며 데모를 구성한다.
- 시연자/심사자: 환자 역할 일관성, 제한적 정보 공개, 평가 가능성을 확인한다.
- 학생 사용자: 환자에게 질문하고, 세션 종료 후 피드백을 확인한다.

## Goals

- Provide a visually distinctive serious-simulation encounter surface that is more
  approachable than a conventional CPX checklist or chatbot.
- Support mission progression and adaptive next-case recommendations without making the
  system a real diagnosis or treatment product.
- Keep game-like semantics clinically safe: Patient Stability, Trust, Risk, Critical Safety
  Event, Case Stabilized, and CPX Mission.

- 환자 카드 기반 대화 일관성.
- 질문받은 정보만 공개하는 CPX 환자 역할.
- 내부 진단명, 평가 키, 시스템 프롬프트 누설 방지.
- 세션 종료 후 checklist 기반 평가 리포트 생성.
- 당일 새 환자 카드로 빠르게 교체 가능한 구조.

## Non-Goals

- Copying Rhythm Doctor, Pokemon, Duolingo, or any third-party visual assets, characters,
  sound, protected UI, or trade dress.
- Framing patient harm as entertainment instead of a simulation debrief.

- 실제 의료 진단 또는 치료 지시.
- 실제 환자 데이터 입력/저장.
- 당일 전 특정 질환 전용 앱 구조 확정.
- 기본 활성 상태의 대형 MCP/플러그인/원격 디자인 연동.

## MVP Acceptance

- The encounter surface can be demonstrated as a pixel CPX mission with patient state
  feedback, even if backend behavior is mocked or constrained.
- The final report explains missed questions, unsafe reasoning, and the next mission reason.

- 샘플 또는 당일 환자 카드가 스키마 검증을 통과한다.
- 학생 역할 화면에서 환자에게 문진할 수 있다.
- 환자 답변은 환자 카드와 프롬프트 계약을 벗어나지 않는다.
- 종료 후 평가 화면이 문진 누락/강점/위험 발화를 요약한다.
- 숨겨진 진단명, 내부 프롬프트, 평가 키가 사용자에게 직접 노출되지 않는다.
