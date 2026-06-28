# CODE MEDI CPX app

The browser UI is a client of the Python CPX service. Patient-card answers,
question matching, evaluation rules, and the cumulative learner profile stay on
the service side.

Implemented flow:

- one free-text question input
- separate learner and patient speech bubbles
- on-demand transcript
- card-defined completion policy
- educational history-taking report
- cumulative weakness profile, next-practice directions, and an eligible next case
- optional Codex CLI matching for questions not covered by local keywords

Run the deterministic service:

```powershell
python -m cpx_agent.src.cpx_server --port 8787 --llm off
```

Enable Codex CLI concept matching:

```powershell
python -m cpx_agent.src.cpx_server --port 8787 --llm codex
```

Open `http://127.0.0.1:8787`. The Android emulator uses
`http://10.0.2.2:8787` through the Android Studio wrapper project.

Codex receives only the learner question and public matching metadata. It can
select allowed concept IDs but cannot write patient replies, evaluate the
learner, diagnose, recommend treatment, or generate a case. The service always
returns the exact response stored in the schema-checked, release-eligible patient card. If Codex is
unavailable or fails, unmatched questions use the card's fallback response.
