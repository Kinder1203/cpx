# CPX Agent Data

`bad_news/` contains the imported 2026-CODE-MEDI bad-news delivery case database
and checklist references. The original source folder is
`C:\Users\user\Desktop\2026-CODE-MEDI\backend`; do not edit that source folder
from this repo. Runtime reports generated from the imported backend go under
`reports/bad_news/`, not inside the imported case DB.

`sessions/` may contain legacy generated learner-profile artifacts from earlier
demo experiments. It is not read by the active bad-news backend and is not a
production clinical-data store.

`reports/` is for generated CPX evaluation reports. The active bad-news backend
adapter writes to `reports/bad_news/`.

Do not store real patient data, private student data, API keys, or secrets here.
