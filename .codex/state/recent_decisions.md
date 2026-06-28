# Recent Decisions

## 2026-06-28 - Evidence-Gated Cards and Resumable Sessions

- Patient-card contract `1.2.0` records a neutral opening line, synthetic fields,
  item-level source coverage, publication status, clinical review status, and formative
  rubric version. Differential concepts use explicit synonym groups.
- Existing chest- and abdominal-pain cards remain `demo_only`; production mode fails
  closed until at least one clinically approved `validated` card exists.
- Sessions now persist in local SQLite and restore after a server restart. Real patient
  or private learner data remains prohibited.
- Codex CLI classification stays optional with low reasoning, an 8-second timeout,
  bounded cache, circuit breaker, and deterministic card fallback.
- Runtime case generation, Graph/Wiki memory, and unreviewed automatic publishing remain
  excluded. Source retrieval tools may assist authoring but do not replace source records
  or clinician approval.

## 2026-06-27 - Guarded Functional Vertical Slice

- Active track is `cpx_agent/`.
- Runtime patient replies come only from schema-checked, release-eligible card text;
  optional Codex CLI is a
  concept-ID classifier, not the patient, evaluator, or case generator.
- Clinical-assessment concept evidence is credited only when disclosed in the current
  encounter; obvious negation and duplicate differential entries do not earn credit.
- Adaptive practice selects deterministically from release-eligible cards. Automatic patient
  generation, Graph/Wiki memory, and self-training remain deferred.
- The 2D pixel serious-simulation design remains unchanged. The report only adds focus
  handling and an existing-style action to start the release-eligible recommendation.
- Codex CLI uses low reasoning only for concept-ID classification; patient text remains
  deterministic card data with local matching and fallback on classifier failure.
- Adaptive practice has two deterministic modes: remediate when important gaps remain,
  otherwise broaden to a different topic. Resolved weaknesses decay, recent cases are
  deprioritized, and uncommon cards require high or critical clinical importance.
- Report findings scroll inside their own list area, while spare encounter height expands
  the existing patient scene rather than changing the visual system.
