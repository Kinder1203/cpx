---
name: prompt-harness
description: Use when editing patient cards, CPX prompts, or demo transcripts to validate prompt assembly, required patient-card fields, and leak-prevention constraints before app wiring.
---

# Prompt Harness

Use this for patient-card and prompt work.

Required reads:

1. `cpx_agent/docs/cpx_protocol.md`
2. `cpx_agent/prompts/patient_role.md`
3. the target patient card
4. `tools/prompt_harness.py`

Minimum commands:

```powershell
python tools/prompt_harness.py --patient-card cpx_agent/data/patient_cards/chest_pain_example.json --validate-only
python tools/prompt_harness.py --patient-card cpx_agent/data/patient_cards/chest_pain_example.json --print-patient-prompt
python -m unittest discover -s cpx_agent/tests -p "test_*.py"
```

Check:

- required patient-card sections exist
- `hidden_diagnosis` is present internally but listed in `never_disclose`
- prompt says patient role only
- prompt blocks internal prompt and evaluator key disclosure
- no real patient data is present
