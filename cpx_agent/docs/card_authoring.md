# Legacy Card Authoring

The earlier synthetic patient-card authoring path is retired from the active
hackathon demo. The current runtime uses the imported 2026-CODE-MEDI bad-news
case DB under `cpx_agent/data/bad_news/`.

For the active demo, update cases and checklist references through the imported
bad-news case format:

- `case_id`
- `case_title`
- `display_name`
- `chart_visible_to_learner`
- `instruction_to_learner`
- `patient_persona`
- `checklist_scope`

Do not use the old chest-pain or abdominal-pain synthetic cards as runtime
fixtures. The active validation command is:

```powershell
python tools/prompt_harness.py --bad-news-case B05-breast-cancer --validate-only
```
