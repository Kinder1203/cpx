# CPX Agent Track

This track prepares the CODE MEDI hackathon demo for the confirmed station:
`bad-news delivery`.

## Product Idea

The learner practices doctor utterances in a CPX-style encounter. The server
uses the imported 2026-CODE-MEDI backend assets to play the standardized
patient, score the completed conversation with checklist/PPI checkpoints, and
generate formative feedback.

This is an educational simulation. It is not a diagnosis, treatment, or
counseling product.

## Minimum Demo Flow

1. The app starts a ready bad-news case from `data/bad_news/cases/`.
2. The learner enters a free-text doctor utterance.
3. The server calls the imported patient-role LLM prompt contract and returns a
   standardized-patient reply.
4. When the encounter ends, the server evaluates the transcript with the
   imported checklist/PPI evaluator prompt contract.
5. The app shows the existing report shape: missed/completed items, feedback,
   weakness analysis, next-practice direction, and next case.

Codex CLI runtime model calls are not part of the demo. Live patient replies and
scoring require `OPENAI_API_KEY`.

## Current Files

- `docs/cpx_protocol.md`: patient role, state, evaluation, and safety contract.
- `data/bad_news/`: copied 2026-CODE-MEDI bad-news cases and checklist reference.
- `src/bad_news_backend.py`: stdlib adapter around the imported backend contract.
- `src/cpx_server.py`: local HTTP API for the browser client and Android WebView.
- `../app/`: browser client.
- `../android/`: Android Studio WebView runner.
- `tests/`: network-free contract tests.

## Validation

```powershell
python tools/healthcheck.py
python -m unittest discover -s cpx_agent/tests -p "test_*.py"
python tools/prompt_harness.py --bad-news-case B05-breast-cancer --validate-only
```

## Run

```powershell
python -m cpx_agent.src.cpx_server --port 8787
```

Browser: `http://127.0.0.1:8787`

Android emulator: `http://10.0.2.2:8787`

Optional model overrides:

- `OPENAI_MODEL_CHAT`
- `OPENAI_MODEL_EVAL`
