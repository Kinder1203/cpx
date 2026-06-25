# Serious Simulation Direction

## Intent

CODE MEDI CPX is a serious simulation that uses game-like accessibility to make CPX
practice feel closer to a live patient encounter without becoming a diagnosis game.

The product should feel like:

- A 2D pixel clinical encounter, not a generic medical chatbot.
- A staged learning journey, not a static quiz.
- A patient-facing CPX practice surface, not a treatment recommendation product.
- A visually memorable demo where the learner improves judgment, communication, and
  red-flag recognition through structured feedback.

## Reference Framing

The references are interaction and presentation references only. Do not copy assets,
characters, UI, names, sound, animations, or protected trade dress.

- Rhythm Doctor reference value:
  - pixel-art medical setting
  - simple controls that become emotionally engaging
  - patient state communicated through motion, rhythm, and screen events
  - stage-based progression with tutorial-like learning
- Pokemon battle-screen reference value:
  - diagonal patient-vs-learner composition
  - opponent/patient focus in the upper-left
  - learner/doctor back-view in the lower-right
  - clear turn-like decision moments
- Duolingo-like reference value:
  - approachable stage map
  - short missions
  - repeated practice loop
  - visible skill progression

## Public Positioning

Use serious-simulation language in user-facing surfaces and presentation.

| Avoid | Use |
| --- | --- |
| HP | Patient Stability |
| Damage | Safety Risk |
| Death ending | Critical Safety Event |
| Game over | Simulation Failed |
| Clear | Case Stabilized |
| Stage | CPX Mission |
| Score | Competency Score |

The learner may make unsafe decisions in the simulation, but the UI should frame this as
clinical learning, not spectacle.

## Core Loop

1. Mission Map
   - The learner selects a CPX mission.
   - Locked missions preview the skill focus, not hidden diagnoses.
2. Case Brief
   - The learner sees safe metadata, chief complaint, and encounter objective.
   - Hidden diagnosis and evaluator keys remain internal.
3. Pixel Encounter
   - Patient appears upper-left.
   - Learner/doctor back-view appears lower-right.
   - The learner asks questions through structured cards, with optional free input.
   - The patient answers only from the patient card and conversation state.
4. State Feedback
   - Patient Stability changes when urgent risks are missed or unsafe reasoning appears.
   - Trust changes with empathy, clarity, and appropriate communication.
   - Risk increases when red flags are ignored or premature closure appears.
5. Decision Board
   - The learner submits differential diagnosis, red flags, next questions, next action,
     and patient explanation.
   - This is educational simulation output, not real-world medical advice.
6. CPX Report
   - Checklist coverage, missed items, communication feedback, safety events, and
     reasoning gaps are shown.
   - Hidden diagnosis can influence evaluation internally but must not be exposed as a raw
     patient-card field or evaluator key.
7. Adaptive Next Mission
   - The system explains which skill weakness drives the next mission recommendation.
   - Full automatic patient generation is optional; a constrained preview or diff is enough
     for demo credibility.

## Interaction Model

Primary input should be structured question cards because they are easier to evaluate,
animate, and demo reliably. Free input may exist as an advanced or assistive layer.

Question cards should map to stable internal concepts:

- checklist_item_id
- information_domain
- empathy_tag
- red_flag_tag
- risk_impact
- trust_impact
- unlock_conditions

Free input should be normalized to one of these concepts before it affects evaluation.

## Visual Contract

The encounter screen should be the signature surface.

- Upper-left: patient sprite, expression/state animation, short patient response bubble.
- Lower-right: learner/doctor back-view sprite, action affordance, selected question state.
- Center/lower area: question cards or decision board controls.
- Top or side status rail: Stability, Trust, Risk, mission objective, safe metadata.
- Bottom transcript drawer: optional, compact, and not visually dominant.

Pixel art should be intentional and restrained:

- 2 to 3 patient sprites are enough for demo setup.
- Each patient needs idle, discomfort, and critical states.
- Animation can be CSS sprite steps, small frame loops, or subtle transform changes.
- Do not rely on AI-generated art unless usage rights and visual consistency are reviewed.
- Do not let art production block the CPX loop.

## Scope Layers

The setup should support the full product vision. Day-of implementation can stop at any
layer that demos well.

### Layer 1: Reliable CPX Core

- patient card validation
- patient-role prompt
- structured question list
- transcript
- checklist evaluation
- report

### Layer 2: Serious Simulation Surface

- mission map
- pixel encounter composition
- patient state meters
- trust/risk/stability updates
- decision board

### Layer 3: Adaptive Learning

- weakness extraction
- next mission recommendation
- patient-card diff preview
- stage progression

### Layer 4: Evidence and Tutor

- curated explanation cards
- optional LLM tutor for missed items
- source links only when curated or validated

## Safety Boundaries

- The learner is practicing CPX reasoning and communication.
- The app is not a real diagnosis or treatment product.
- The patient persona does not provide medical authority.
- Critical Safety Event is a simulation debrief state.
- Hidden diagnosis, evaluator keys, internal prompts, and raw patient-card internals are not
  rendered in UI, downloads, screenshots, or demo logs.

## Design Setup Implications

- `design.md` owns tokens and component rules.
- `wireframes.md` owns layout contracts.
- `functional_spec.md` owns objects and behavior.
- `user_flows.md` owns learner/admin/demo flows.
- Figma can be used after a specific frame or community file is selected.
- Playwright or browser QA should validate the encounter screen at desktop and mobile sizes.

## Demo Success Criteria

The demo is working when a judge can understand this in under three minutes:

1. This is a CPX patient encounter, not a chatbot.
2. The learner's questions change patient trust, risk, and stability.
3. Missed clinical reasoning steps are visible in the final CPX report.
4. The next mission is justified by the learner's weakness.
5. The visual style makes practice approachable without trivializing patient safety.
