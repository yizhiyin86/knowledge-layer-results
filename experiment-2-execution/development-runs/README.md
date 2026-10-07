# Development runs (not part of the reported results)

Single runs made while building the benchmark. They are kept because they show how the task set and the process model were corrected before the reported runs. Earlier code versions; numbers here are not results.

| Folder | What it was for |
|---|---|
| `execution_dry1/` | First end-to-end run of Agent B on T1 (before the approval threshold change). |
| `execution_dry2/` | A on T1; B on T2, T3, T6, T7, T8. Found that the first T6/T7 scenario was wrong (the materials were used at one plant only, so the backup supplier covered everything). |
| `execution_dry3/` | A and B on the corrected T6, then B on T7. B treated the partial approval as covered (no discovery). |
| `execution_dry4/` | B on T6 → review → T7 after the process branch conditions were made precise: first full learning loop. |
| `execution_dry5/` | B on T1 after the approval threshold changed to $25,000 per DC plan: verifies approval before writing. |
