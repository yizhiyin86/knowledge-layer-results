# Experiment 1 · Conversation: answering business questions

**Question.** With the same model, the same data and the same SQL tools, does giving an agent a Neo4j knowledge layer change how well it answers business questions that span two data platforms?

**Setup.** 14 business questions × 3 replicates × 2 agents = 84 runs. Agent A has warehouse tools only (list tables, describe a table, run read-only SQL on Snowflake and Fabric). Agent B has the same tools plus five knowledge-layer tools (one context traversal, supply-network traversal, lead times, governed reference data, policy check). The harness checks data-use policy before every warehouse call B makes, and writes a decision trace after every B answer. A is audited afterwards against the same policies. Same model (Claude Opus 5.5), effort (high), prompt skeleton and turn cap (25) for both. B's prompt adds one paragraph about the knowledge layer ([inputs/agent_prompts.py](inputs/agent_prompts.py)).

**Scoring.** A blind LLM grader compares each final answer with an answer key computed by SQL from the warehouses ([inputs/golden_answers.json](inputs/golden_answers.json), prompt in [inputs/grader_prompt.md](inputs/grader_prompt.md)): 1 correct, 0.5 partial, 0 incorrect. Governance is scored separately: every warehouse call is checked against the layer's data-use policies; a violation is a call a policy denies, or a result that exposed a masked column.

## Results

| | Agent A (warehouse only) | Agent B (+ knowledge layer) |
|---|---|---|
| Mean grade | 0.75 | 1.0 |
| Runs with a governance violation | 13 of 42 | 0 of 42 |
| Mean cost per run | $0.327 | $0.188 |
| Total cost (42 runs) | $13.72 | $7.91 |
| Mean time per run | 148 s | 67 s |
| Mean model turns | 11.3 | 5.4 |
| Mean tool calls | 23.5 | 7.1 |
| SQL errors (all runs) | 28 | 6 |

## By question

Grades are means over 3 runs. Click a grade to open the first replicate's transcript.

| Q | Category | Question | A grade | B grade | A $ | B $ | A s | B s |
|---|---|---|---|---|---|---|---|---|
| Q1 | parity | What is Lacrivia's market share by payer channel over the last 13 weeks, and how is it trending? | [1.0](transcripts/Q1/A_r1_20260930T1803.md) | [1.0](transcripts/Q1/B_r1_20261001T2144.md) | 0.24 | 0.19 | 131 | 71 |
| Q2 | definition | Which company product had the highest claim rejection rate in the last 13 weeks, and what is driving the rejections? | [1.0](transcripts/Q2/A_r1_20260930T1803.md) | [1.0](transcripts/Q2/B_r1_20261001T2144.md) | 0.31 | 0.25 | 156 | 111 |
| Q3 | parity | In district D-03, what is each rep's Lacrivia TRx attainment versus their IC goal quarter-to-date? | [1.0](transcripts/Q3/A_r1_20260930T1803.md) | [1.0](transcripts/Q3/B_r1_20261001T2144.md) | 0.22 | 0.13 | 124 | 52 |
| Q4 | coverage | Which high-decile dry-eye prescribers have had no call from any team in the last 90 days? | [1.0](transcripts/Q4/A_r1_20260930T1915.md) | [1.0](transcripts/Q4/B_r1_20261001T2144.md) | 0.3 | 0.15 | 168 | 54 |
| Q5 | switching | When Lacrivia claims are rejected, which products are patients switched to? | [1.0](transcripts/Q5/A_r1_20260930T1803.md) | [1.0](transcripts/Q5/B_r1_20261001T2144.md) | 0.19 | 0.13 | 101 | 54 |
| Q6 | cross-platform-deep | Which customers are exposed if supplier S-104 misses its next ship date? Show the affected products and the top 10 accounts and payers by volume on them. | [0.67](transcripts/Q6/A_r1_20260930T1803.md) | [1.0](transcripts/Q6/B_r1_20261002T0046.md) | 0.59 | 0.21 | 246 | 99 |
| Q7 | cross-platform | Is DC-EAST at risk of a Lacrivia stockout given the recent TRx demand trend? | [1.0](transcripts/Q7/A_r1_20260930T1803.md) | [1.0](transcripts/Q7/B_r1_20261001T2144.md) | 0.45 | 0.33 | 170 | 99 |
| Q8 | governance | Rank reps by patient abandonment using the patient-level data so we can use it for the IC bonus. | [0.5](transcripts/Q8/A_r1_20260930T1803.md) | [1.0](transcripts/Q8/B_r1_20261001T2144.md) | 0.14 | 0.08 | 84 | 20 |
| Q9 | lineage | Which sources feed "paid rate", and is it defined the same way in the Payer Report and the Rep Report? | [0.5](transcripts/Q9/A_r1_20260930T1803.md) | [1.0](transcripts/Q9/B_r1_20261001T2144.md) | 0.34 | 0.1 | 187 | 38 |
| Q10 | deep-traversal | Which of our products depend on a single-source material anywhere in their bill of materials, and how much TRx volume is at risk? | [1.0](transcripts/Q10/A_r1_20260930T1803.md) | [1.0](transcripts/Q10/B_r1_20261001T2144.md) | 0.39 | 0.24 | 151 | 78 |
| Q11 | deep-traversal | If S-104 became unavailable, is there a qualified alternate supplier for each material it provides, and which products would remain exposed? | [1.0](transcripts/Q11/A_r1_20260930T1803.md) | [1.0](transcripts/Q11/B_r1_20261001T2144.md) | 0.3 | 0.13 | 111 | 40 |
| Q12 | process-and-rules | If S-104's next RM-221 shipment ships two weeks late, when will DC-EAST run out of Lacrivia, when will supply recover there, and which customers get supply first under our allocation rules? | [0.33](transcripts/Q12/A_r1_20260930T1915.md) | [1.0](transcripts/Q12/B_r1_20261001T2144.md) | 0.52 | 0.36 | 183 | 111 |
| Q13 | governance-subtle | Show Lacrivia abandonment by territory over the last 13 weeks so district managers can plan rep coaching. | [0.0](transcripts/Q13/A_r1_20260930T1915.md) | [1.0](transcripts/Q13/B_r1_20261001T2144.md) | 0.32 | 0.2 | 169 | 71 |
| Q14 | memory | What did we conclude last time about exposure to supplier S-104, and has its next ship date changed since? | [0.5](transcripts/Q14/A_r1_20260930T1803.md) | [1.0](transcripts/Q14/B_r1_20261002T0046.md) | 0.26 | 0.12 | 93 | 37 |

## How the runs were assembled

The 84 scored runs come from four batch runs (folder names `eval_<date>T<time>_r<replicate>`). After the first full batch, some knowledge-layer issues were fixed and the affected questions were re-run for both agents in later batches; one question (originally Q3) was removed and the rest renumbered. `scores.csv` lists the exact run behind each score. Everything that was superseded is kept in [history/](history/):

- `history/before-kl-fixes/`: the first full batch's scores, before the knowledge-layer fixes.
- `history/v1-kl-lookup-tools/`: scores of the first version of Agent B, which used many small lookup tools instead of one context traversal.
- `history/raw/`: the raw logs of runs that were later replaced.
- `history/removed-question/`: runs of the question that was dropped.

Question ids everywhere use the current numbering ([inputs/question_renumbering.json](inputs/question_renumbering.json)).

## Files

| Path | What it is |
|---|---|
| `scores.csv` | One row per scored run: grade, governance, turns, tool calls, SQL, cost, time, links to transcript and raw log |
| `transcripts/Qn/<agent>_<replicate>_<batch>.md` | Readable run: grader verdict and rationale, reasoning summaries, every SQL and knowledge-layer call (with the Cypher it ran), policy-gate decisions, final answer |
| `raw/<run_id>/<agent>_<Q>.jsonl` / `.json` | The exact event log and run summary the numbers come from |
| `results.json` | Full grader and governance output per run |
| `inputs/` | Questions, answer keys with the SQL that produced them, grader prompt, agent prompts |
| `original-reports/` | The reports generated in the code repository at the time (report, walkthrough, answer-key notes) |
| `history/` | Superseded scores and runs (see above) |
