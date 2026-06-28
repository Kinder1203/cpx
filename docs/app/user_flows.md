# User Flows

## Flow 1: Prepare Case

1. The server loads playable cases from `cpx_agent/data/bad_news/cases/`.
2. The app receives only public case metadata and learner-facing chart content.
3. Hidden diagnosis, checklist keys, internal prompts, and evaluator rubrics stay server-side.

## Flow 2: Run Encounter

1. The learner starts a selected bad-news case.
2. The learner enters a free-text doctor utterance.
3. The server sends the transcript and imported case persona to the patient-role LLM.
4. The patient reply is appended to the session transcript.
5. The learner continues or ends the encounter.

## Flow 3: Evaluate

1. The server evaluates the final transcript with checklist and PPI evaluator prompts.
2. The report returns completed/missed checklist items, feedback, weakness summary, and next-practice direction.
3. The app renders only educational feedback, not hidden case internals.

## Flow 4: Next Practice

1. The server recommends remediation or progression based on missed checkpoint categories.
2. The learner can start the recommended next case from the same API flow.

## Flow 5: Backend Case Update

1. Add or update imported bad-news case JSON under `cpx_agent/data/bad_news/cases/`.
2. Validate with `python tools/prompt_harness.py --bad-news-case B05-breast-cancer --validate-only`.
3. Run `python tools/healthcheck.py` and the unit test suite.
