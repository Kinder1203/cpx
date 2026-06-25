# Functional Specification

## Core Objects

- Patient Card: synthetic CPX case source of truth.
- Encounter Session: one student-user conversation with a patient persona.
- Transcript: timestamped messages for evaluation.
- Evaluation Report: checklist and safety summary after the encounter.
- CPX Mission: a staged learning unit with safe metadata, objective, difficulty, and skill
  focus.
- Patient State: visible simulation state made from Patient Stability, Trust, and Risk.
- Decision Board: structured learner submission for differential diagnosis, red flags, next
  action, and patient explanation.
- Weakness Profile: post-encounter summary used to recommend or generate the next mission.

## MVP Screens

1. Mission Map
   - Show CPX missions, lock states, difficulty, and skill focus.
   - Do not reveal hidden diagnosis or evaluator keys.
2. Case Setup
   - Load/select patient card.
   - Show only safe case metadata.
   - Validate required card sections before starting.
3. Pixel Encounter
   - 2D patient-facing scene with patient upper-left and learner back-view lower-right.
   - Structured question cards as the primary input.
   - Optional free-text input only after it can be normalized to checklist concepts.
   - Patient role only; no diagnosis/treatment authority.
   - Visible Patient Stability, Trust, Risk, and end-session control.
4. Decision Board
   - Submit suspected diagnosis, differential diagnoses, red flags, next action, and patient
     explanation for educational evaluation.
5. Evaluation
   - Checklist coverage.
   - Missed questions.
   - Communication notes.
   - Safety/leak flags.
   - Weakness-driven next mission reason.
6. Demo Admin
   - Reset session.
   - Swap patient card.
   - Export synthetic session/report only when requested.

## Guarded Behaviors

- The app must not render `hidden_diagnosis`, evaluator answer keys, or internal prompts.
- If a user asks for diagnosis or treatment, the patient role should stay in patient boundary
  and route to safety guidance.
- If a user asks for unavailable facts, the patient must not invent details outside the card.
- Logging must not include secrets, real patient data, or API keys.
- Critical Safety Event is a debrief state, not entertainment or real-world outcome prediction.
- Patient state changes must be explainable from checklist, red-flag, communication, or safety
  rules.

## Deferred Decisions

- Frontend framework.
- LLM provider and model.
- Backend/runtime packaging.
- Authentication.
- Remote deployment.
- Persistent database.

These decisions are made only after the hackathon topic, time, and team constraints are known.
