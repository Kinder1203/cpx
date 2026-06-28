# CPX Agent Data

`patient_cards/` contains synthetic scenario inputs. These are source inputs for
the demo, not real patient records.

`sessions/` is for generated learner profiles and the local SQLite session/event store.
The store supports restart recovery for this single-user demo; it is not a production
clinical-data store.

`reports/` is for generated CPX evaluation reports.

Do not store real patient data, private student data, API keys, or secrets here.
