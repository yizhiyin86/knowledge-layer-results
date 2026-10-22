# Experiment 3: commercial banking (conversation pattern)

The same A/B design as experiment 1, rebuilt for a fictional US commercial bank. Same model, same prompt, same warehouse tools for both agents; Agent B also has a Neo4j enterprise knowledge layer. All data is synthetic; the bank, companies and people are fictional, and the credit policy is simplified for illustration.

## Setup

| | |
|---|---|
| Model | Claude Opus 5.5 (Azure AI Foundry), same prompt skeleton and effort for both agents, up to 25 turns |
| Agent A | Warehouse tools only: list tables, describe a table (columns + 5 sample rows), read-only SQL |
| Agent B | The same tools + 4 knowledge-layer tools over MCP: `get_context` (one traversal across the layers), `trace_obligor_group` (ownership hierarchy), `get_reference`, `check_policy`. A policy gate checks every warehouse call; a decision trace is written after every answer |
| Snowflake `BANK_DEMO` | Commercial banking: clients (CIF), relationship managers, contacts, goals, credit facilities and month-end balances, deposits, reference codes, sector map, marts, restricted suspicious-activity cases, sandbox copies (21 tables, 82K rows) |
| Fabric `RISK_DEMO` | Risk and capital markets: legal entities, ownership up to 7 levels with dates, agency ratings, derivatives exposure, group limits, guarantees, covenants, a stale legacy hierarchy (9 tables, 10K rows) |
| Knowledge layer | Neo4j Aura, about 5,100 nodes and 9,700 relationships: six layers (process and rules, domain semantics aligned to FIBO/LEI/NAICS, data products and OSI metrics, physical systems harvested from both catalogs, tools, memory) plus the ownership hierarchy as the data slice |

Showcase scenario: Halvorsen Industrial Group (LE-10001) is downgraded by agency AGY1 from BB- to CCC+ on 2026-09-28. Its obligor group has 24 controlled entities up to 7 levels deep and $344.3M of exposure.

## Questions and scoring

14 questions (`questions.yaml`) in three types: simple single-source (Q1–Q5), cross-source and deep traversal (Q6, Q7, Q10–Q12), governance and business meaning (Q8, Q9, Q13, Q14). Each was run 3 times per agent (84 graded runs).

- **Accuracy:** answer keys computed with SQL (`golden_answers.json`); an LLM grader that does not know which agent answered scores each answer 1 / 0.5 / 0 against the key and the check rule.
- **Governance:** every warehouse call of both agents is audited against the same data-use policies (B at run time, A afterwards).
- **Cost:** Claude tokens at list price; warehouse and Neo4j compute excluded. **Time:** wall-clock seconds per answer.

## Results

| | Agent A | Agent B |
|---|---|---|
| Accuracy | 0.77 | **1.00** |
| Cost per answer | $0.28 | **$0.15 (−47%)** |
| Time per answer | 123 s | **52 s (−58%)** |
| Runs with a policy violation | 5 of 42 | **0 of 42** |

| Question type | Accuracy A → B | Cost | Time | Violations |
|---|---|---|---|---|
| Simple (Q1–Q5) | 1.00 → 1.00 | −25% | −52% | 0 → 0 of 15 |
| Cross-source & deep traversal (5) | 0.80 → 1.00 | −56% | −58% | 0 → 0 of 15 |
| Governance & business meaning (4) | 0.46 → 1.00 | −50% | −65% | 5 → 0 of 12 |

Per question: `report.md`, `results.csv`, `numbers.json`.

**What drove the difference.** Agent A is a strong analyst: it walked the 7-level ownership tree level by level after Fabric rejected its recursive SQL (error 8768), and it refused to rank bankers by suspicious-activity reports (public law). Its misses were knowledge that is in no warehouse: how two reports define the NPL ratio (Q9), the bank's rating map and lending-authority matrix (Q12), the eligible-guarantee rule (Q11), an internal entitlement on RM goals (Q13, A 0 of 3), and memory of an earlier answer (Q14). B was right on every question and about twice as fast and cheaper.

## What B knew that A didn't (by design)

Credit policy (legal lending limit, rating map, delegated lending authority, eligible guarantees, rating triggers), the report definitions of NPL, internal entitlements, curated table and column descriptions, ratified metrics and join rules, and memory. This knowledge lives in policy manuals and people's heads, which is the case for a knowledge layer.

## Changes during the experiment (all disclosed)

1. After replicate 1, **Q7 was reworded** (it was ambiguous: B rolled clients up to their groups under the layer's obligor-group rule) and **Q13 was replaced** (the original asked about suspicious-activity data, which a model already knows is restricted by law; the new Q13 tests an internal entitlement). Both were fully re-run for both agents.
2. A bug in B's `trace_obligor_group` tool (a date it could not serialize) made the tool fail whenever the group's parent had a rating; B still scored 1.00 by falling back on other tools. After the fix, **B was re-run on the six affected questions** (Q6, Q7, Q10, Q11, Q12, Q14). A was not changed. Before the fix B's overall results were 0.98 accuracy, $0.17 and 53 s per answer.

The replaced runs are kept in `runs-superseded/`.

## Files

| Path | Contents |
|---|---|
| `questions.yaml` | The 14 questions, requester roles and check rules |
| `golden_answers.json` | Answer keys with the SQL that produced them |
| `results.json`, `results.csv`, `report.md` | Graded results per run, with grader rationale and governance audit |
| `numbers.json` | Aggregates used on the slides |
| `runs/<batch>_r<n>/` | The 84 graded runs: `<agent>_<question>.json` (summary) and `.jsonl` (every model turn and tool call, with SQL and Cypher) |
| `runs-superseded/` | The 30 replaced runs (see above) |
| `queries/why_a_graph_layers.cypher` | One traversal across the layers, from B's Q12 decision trace to the data (1 row, 14 nodes, ~4 ms on Aura) |

Batches: `eval_20261022T0005` = main run (A all questions; B unchanged questions); `eval_20261022T0035` = Q7 and Q13 re-run (both agents); `eval_20261022T0047` = B re-run after the tool fix.

## Limitations

Synthetic, small and simplified: two platforms, 30 tables, one bank's worth of illustrative rules, 3 runs per question. Exposure ignores netting, potential future exposure and collateral. The test shows the mechanism; a proof of concept on a customer's own questions is what proves it there.
