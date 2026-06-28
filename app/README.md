# CODE MEDI CPX app

The browser UI is a client of the Python CPX service. Patient cases, bad-news
delivery checkpoints, PPI scoring, report generation, and next-practice
recommendations stay on the service side.

Implemented flow:

- one free-text doctor utterance input
- separate learner and patient speech bubbles
- on-demand transcript
- server-generated standardized-patient replies from the imported bad-news case DB
- checkpoint/PPI-based report after the encounter ends
- cumulative weakness profile, next-practice directions, and an eligible next case

Run the service:

```powershell
python -m cpx_agent.src.cpx_server --port 8787
```

Open `http://127.0.0.1:8787`. The Android emulator uses
`http://10.0.2.2:8787` through the Android Studio wrapper project.

Live patient utterance generation and scoring require `OPENAI_API_KEY` because
the server calls the imported 2026-CODE-MEDI bad-news backend prompt contract.
This app still does not call Codex CLI at runtime.
