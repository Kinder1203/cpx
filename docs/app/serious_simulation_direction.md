# Serious Simulation Direction

## Intent

CODE MEDI CPX is a 2D pixel CPX serious simulation. Pixel art makes the encounter
approachable, while the patient-card, disclosure, and evaluation contracts remain clinical
and deterministic. It is not a diagnosis game or a plain chatbot.

## Active Direction

- The encounter is the first and primary screen.
- The patient occupies the upper-left and the learner back-view the lower-right.
- Learner and patient speech are both visible and clearly distinguished.
- Free-text questioning is the only learner-facing history-taking input.
- The transcript supports the scene without becoming the whole product.
- Evaluation follows the encounter and remains inside a bounded app sheet.
- Adaptive behavior means weakness-based next-case selection, not unrestricted generation.

## Retired From The Active Contract

Mission Map, structured question cards, Patient Stability, Trust, Risk, Critical Safety
Event, and turn-like battle semantics are not active UI requirements. They may remain
historical design vocabulary only and must not drive implementation or tests.

## Visual Contract

- Use original pixel assets and a restrained clinical education palette.
- Keep product controls readable rather than rendering every control as pixel art.
- Use motion only for patient/learner presence or clear interaction feedback.
- Do not expose rubric progress, hidden answers, or internal safety invariants as status HUDs.
- Do not copy third-party game assets, characters, layouts, sound, or trade dress.

## Safety Boundaries

- The learner practices history-taking and educational reasoning.
- The patient persona does not diagnose or recommend treatment.
- Hidden diagnosis, evaluator keys, internal prompts, and raw card internals never render in
  learner-facing UI or public payloads.
- Patient-card-specific feedback does not require a paper citation. External evidence is used
  only when it directly supports the feedback claim and has been curated.

## Demo Success Criteria

1. A reviewer recognizes a CPX patient encounter rather than a generic chatbot.
2. Questions reveal only relevant information from an eligible patient card.
3. Learner and patient dialogue form an auditable transcript.
4. The report explains omissions and the next practice target.
5. Browser and Android layouts remain inside the app frame without overlap.
