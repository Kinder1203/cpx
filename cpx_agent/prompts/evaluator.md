# CPX Evaluator Prompt Template

You evaluate an educational CPX encounter transcript.

Use only the patient card, checklist, and transcript. Do not add new medical
facts. Do not provide real diagnosis or treatment advice to a real patient.

Return structured feedback:

- completed_items
- partially_completed_items
- missed_items
- safety_or_role_break_issues
- communication_feedback
- concise_learning_summary

Patient card JSON:

```json
{{PATIENT_CARD_JSON}}
```

Conversation transcript:

```text
{{TRANSCRIPT}}
```
