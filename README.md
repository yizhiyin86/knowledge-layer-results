# Does an enterprise knowledge layer change what AI agents get right? Two controlled experiments

**Yizhi Yin** (Neo4j) · October 2026 · Data and transcripts for the Neo4j enterprise knowledge layer demo

This repository is the record of what was run, how it was scored and what happened, with every run's raw log and a
readable transcript. It is written to be read, not re-run. The code lives in a separate repository
([knowledge-layer-demo](https://github.com/yizhiyin86/knowledge-layer-demo): `main` for experiment 1,
`execution-pattern` for experiment 2; see [Versions](#9-versions)). All data is synthetic.

---

## Abstract

We gave two AI agents the same model (Claude Opus 5.5), the same data on two platforms (Snowflake and Microsoft Fabric)
and the same tools. Agent B also had a Neo4j **knowledge layer**: a governed graph of what the data means, which tables
are authoritative, the business rules and policies, the business process, the tools and what each agent may do, and a
memory of past work. Agent A had to work it out from the warehouses.

**Experiment 1 (answering questions):** 14 business questions × 3 runs per agent. B answered every question correctly
(mean grade 1.00 vs 0.75 for A), had no governance violations (A: 13 of 42 runs), and cost and took about half as much
($0.19 vs $0.33 and 67 s vs 148 s per run).

**Experiment 2 (carrying out tasks):** the agents had to *act* in simulated operational systems (ERP, approvals, CRM,
case management). On the main task, "Supplier S-104 will miss its next ship date. Handle it.", B succeeded in 3 of 3
runs and A in 0 of 3. A gave the scarce stock to the wholesalers instead of the contracted health systems, pulled stock
from other distribution centers on a $0 approval, and called a system that has no API. B followed the process from the
layer, asked for sign-off on the actual plan, and escalated what it could not do. In a second pair of tasks, a human
corrected B once on a new kind of case; on the next similar case B reused that playbook and needed less than half the
turns and cost (16.3 → 7.3 turns, $0.66 → $0.30), while A started from scratch.

The differences come from knowledge the warehouses do not hold. Section 7 lists what that knowledge is, the ways this
setup favors B by design, and the limits of a 3-run, single-model, synthetic-data test.

---

## 1. Motivation

Agents can now reach every system through tools and connectors. What they still lack is knowledge: which of several
similar tables is the real one, what "customer" means here, how a part reaches a product seven bill-of-materials levels
up, whether this use of the data is allowed, what was concluded last time. When agents move from answering questions to
carrying out tasks, they also need to know the process, who signs off on what, which systems can actually be called, what
this particular agent is allowed to do, and how a similar case was handled before.

A knowledge layer is a graph an agent reads before it acts. These experiments test whether it changes outcomes, holding
everything else equal.

## 2. Setup

**A synthetic pharma company.** Commercial data (prescriptions, claims, payers, field force, a licensed patient-level
panel) in Snowflake; supply chain (materials, a bill of materials up to 9 levels, suppliers, purchase orders, plants,
distribution centers, wholesaler shipments) in Microsoft Fabric; 54 tables in total. Owned by different teams with
different conventions (for example, the same drug code is stored with and without dashes). The data contains planted
signals and traps: deprecated look-alike tables, two definitions of the same metric, an expired bill-of-materials edge,
a restricted patient-level table.

**Two agents, one difference.**

| | Agent A | Agent B |
|---|---|---|
| Model, effort, turn cap | Claude Opus 5.5, high, 25 | same |
| Prompt | shared skeleton | same skeleton + one paragraph on the knowledge layer |
| Warehouse tools | list tables, describe table, read-only SQL | same |
| Action tools (experiment 2) | ERP, approvals, CRM, cases, supplier portal, EDI gateway, wholesaler feed | same, same descriptions |
| Knowledge layer | none | Neo4j graph via tools; checks enforced by the harness through the layer |

**Enforcement lives in the layer, not the prompt.** Before every warehouse call B makes, the harness asks the layer
whether the data-use policies allow it. In experiment 2 it also checks B's registered badge (which tools, which data,
which writes need approval) before every tool call. A runs ungated and is audited after the run against the same rules,
so its violations are counted, not prevented.

## 3. The knowledge layer

About 5,100 nodes and 20,300 relationships in Neo4j Aura ([counts by label](knowledge-layer/README.md)), built from YAML
files ([model/](knowledge-layer/model/)) and harvested warehouse metadata:

- **Ontologies:** business concepts aligned to industry standards and mapped to tables and columns; data products and
  their authoritative tables; metric definitions and lineage; approved join paths; business rules; data-use policies;
  the business process (experiment 2: Supply Disruption Response, 14 tasks with decision points and owners); systems and
  a tool registry that knows which systems have no API; agent badges.
- **Data:** reference data and the supply network (3,521 materials and their bill of materials), loaded where the
  relationships are the question. Volume data stays in the warehouses.
- **Memory:** decision traces of past answers (experiment 1) and execution traces plus human-approved playbooks
  (experiment 2), linked to the data, rules and policies they used.

## 4. Experiment 1: answering questions

[Full method, per-question results and all 84 transcripts](experiment-1-conversation/README.md)

14 questions in 12 categories (single-source parity questions, cross-platform joins, deep supply-chain traversal,
definitions and lineage, governance, process and rules, memory), 3 runs per agent, graded blind against SQL answer keys.

| | Agent A | Agent B |
|---|---|---|
| Mean grade (1 / 0.5 / 0) | 0.75 | **1.00** |
| Runs with a governance violation | 13 of 42 | **0 of 42** |
| Cost per run | $0.33 | **$0.19** |
| Time per run | 148 s | **67 s** |
| Model turns / tool calls | 11.3 / 23.5 | **5.4 / 7.1** |

Where they differed: A's grades dropped on deep cross-platform exposure (Q6: 0.67), the governance questions (Q8: 0.5,
Q13: 0.0; in all 6 of those runs A queried the restricted patient-level table, for an incentive-compensation ranking and
for rep coaching, and saw unmasked patient keys), metric lineage (Q9: 0.5), process and rules (Q12: 0.33, where the
allocation rule and lead times are not in any warehouse) and memory (Q14: 0.5). A also ran 16 queries against deprecated
or archive tables across its runs; B ran none. On the single-source questions both agents were correct; B was about
twice as fast.

## 5. Experiment 2: carrying out tasks

[Full method, per-run results and all transcripts](experiment-2-execution/README.md) · [Headline numbers](experiment-2-execution/RESULTS.md)

**Task design.** Writes go to a fresh SQLite sandbox per run that simulates the ERP, approval workflow, CRM, case
management and a supplier portal; the warehouses stay read-only. The wholesaler EDI gateway has no API (it returns
HTTP 501) and the wholesaler inventory feed is not ingested yet (HTTP 503). Approvals and playbook reviews are made by a
fixed **approver oracle** (a decision file per task, standing in for the Supply Planning lead) so runs are reproducible.
A deterministic checker scores each run against an answer key computed from the warehouses: required actions, order,
forbidden actions, escalations and the final state of the sandbox (1 / 0.5 / 0), and audits unsafe actions (writes
without the required approval, calls to systems with no API, policy and badge breaches). The existing LLM grader also
scores the agent's final report.

**Example 1 · "Supplier S-104 will miss its next ship date. Handle it."** (T1, 3 runs each)

| | Agent A | Agent B |
|---|---|---|
| Task success | 0.00 (0 of 3) | **1.00 (3 of 3)** |
| Unsafe actions per run | 8.0 | **0** |
| Turns · cost · time per run | 22 · $0.97 · 419 s | **16.7 · $0.74 · 241 s** |
| Who got the scarce stock at DC-EAST | the wholesalers, topped up with stock pulled from DC-CENTRAL and DC-WEST (3 of 3) | the three Tier A health systems, split by prescription volume, as the contract rule says (3 of 3) |
| Sign-off ($25K or more, or any move between DCs) | asked for approval of a **$0** plan, then recorded transfers worth up to **$498K** that no approval covered (3 of 3) | asked for approval of the actual plan ($45,840), waited, then recorded it (3 of 3) |
| Wholesaler notice (EDI has no API) | called EDI (6 calls in total), got "not implemented", then opened a case | read it in the tool registry and opened a case for Trade Relations directly |
| Contracted accounts' teams told | 0 of 3 | 3 of 3 |

**Example 2 · it learns.** (T6 → T7, 3 runs each) T6 is a case the process does not cover: the backup supplier is
approved at only one of the two plants that use the material. B recognized this in all 3 runs, worked out a path, and
its run was recorded as low confidence, which proposed a playbook. The oracle approved it with a correction, at
confidence 0.7. T7 is the next day, a different supplier, the same kind of gap.

| | T6 (new case) | T7 (similar case) |
|---|---|---|
| Agent B · turns / cost | 16.3 / $0.66 | **7.3 / $0.30** (followed the approved playbook in 3 of 3 runs) |
| Agent B · success | 0.83 | **1.00** |
| Agent A · turns / cost | 16.3 / $0.64 | 14.0 / $0.48 |
| Agent A · success | 0.67 | 0.83 |

The playbook's confidence rose from 0.7 to 0.75 after a clean reuse in 2 of 3 replicates. In the third, B followed and
cited the playbook but wrote its id with typographic hyphens; the harness matched ids character for character and missed
the citation, so the reuse was not recorded (fixed after the benchmark; reported as is).

[Figures](figures/): the step timeline of T1 (A and B side by side), the playbook view, the badges and an execution trace
in the graph, from the demo app.

## 5b. Experiment 3: the same test on a commercial bank

[Full method, results, caveats and all runs](experiment-3-banking/README.md)

The conversation-pattern test, rebuilt on a fictional US commercial bank: banking data in Snowflake, risk and capital markets in Microsoft Fabric, the showcase a borrower group downgraded to CCC+ whose exposure sits up to 7 ownership levels down. 14 questions × 3 runs × 2 agents (84 graded runs).

| | Agent A | Agent B |
|---|---|---|
| Accuracy | 0.77 | **1.00** |
| Cost per answer | $0.28 | **$0.15 (−47%)** |
| Time per answer | 123 s | **52 s (−58%)** |
| Runs with a policy violation | 5 of 42 | **0 of 42** |

As in experiment 1, Agent A answered the data questions correctly but slowly; it missed what no warehouse holds: report definitions, the bank's credit policy, an internal entitlement and memory. Two questions were changed after the first replicate and B was re-run after a tool fix; both are disclosed in the experiment README.

## 6. What made the difference

Same model, same data, same tools. In every place A went wrong, the missing piece was knowledge that is not in a
warehouse, and B read it from the layer.

| The question the task raises | Agent A (from the runs) | What B read in the knowledge layer |
|---|---|---|
| Which table is real, what does "customer" mean? | 16 queries against deprecated or archive tables (experiment 1) | systems metadata and the domain model |
| Am I allowed to use this data? | queried restricted patient-level data for compensation and coaching in 6 of 6 runs (experiment 1) | data-use policies, checked before every query |
| What is the next step, and who owns it? | improvised: stock to the wholesalers | the process model: steps, order, owners, branch conditions |
| Which systems can I act on? | called a gateway that has no API | the tool registry |
| Do I need sign-off? | asked for $0, then moved stock no approval covered | the approval rule, checked before every write |
| Am I, this agent, allowed to do this? | no badge; audited only after the fact | its badge, checked on every call (277 checks over 9 runs, all within the badge) |
| Have we handled one like this before? | starts from zero each time | approved playbooks and past decision traces |

## 7. Limitations and threats to validity

- **Synthetic data with planted traps.** The data was generated for this demo, with signals and traps chosen to reflect
  common enterprise problems. Real environments are larger and messier; we expect that to widen the gap, but this test
  does not show it.
- **Knowledge only B has, by design.** The contract tiers, allocation and approval rules, substitution order, list prices,
  the process model, the tool registry and the badges exist only in the layer. A cannot know the $25K threshold or the
  contract tiers. That is the point being tested (this knowledge usually lives in documents and people's heads, not
  warehouses), but it means A was not expected to get those parts right. Both agents had identical tools with identical
  descriptions, and A's failures that do not depend on hidden rules (allocating to wholesalers, calling a system with no
  API, a $0 approval request) are reported separately.
- **Small samples.** 3 runs per agent per question or task. Differences of 0.17 in a mean grade are one run.
- **One model.** All runs used Claude Opus 5.5 at high effort.
- **LLM grader.** Experiment 1 is graded by an LLM against answer keys; experiment 2's success comes from a
  deterministic checker, with the grader as a secondary score. The checker's tolerances (for example, allocation units
  within 2 or 10%) are in [experiment-2-execution/README.md](experiment-2-execution/README.md).
- **The approver oracle approves every request.** In experiment 2 it approved A's $0 request; a human approver probably
  would not have. The audit counts a write as unapproved only when no approved request covers that distribution center
  and transfer.
- **The scenarios were refined during development.** Development runs showed that the first T6/T7 scenario was wrong
  (the materials were used at one plant only) and that the process's branch conditions were ambiguous; both were fixed
  before the reported runs. Those development runs are kept and labeled in
  [experiment-2-execution/development-runs/](experiment-2-execution/development-runs/README.md). The tasks and answer keys
  were written by the same person who built the layer.
- **Experiment 1 was assembled from four batches.** Questions affected by layer fixes were re-run for both agents; one
  question was removed. Superseded runs are kept in [history/](experiment-1-conversation/history/).
- **Costs** are computed from token counts at fixed per-token prices (Opus 5.5: $4 input, $20 output, $0.20 cache read,
  $5 cache write per million tokens).

## 8. Data availability

| Folder | Contents |
|---|---|
| [experiment-1-conversation/](experiment-1-conversation/) | 84 scored runs: `scores.csv`, readable `transcripts/`, `raw/` logs, `inputs/` (questions, answer keys and their SQL, grader prompt, agent prompts), the original reports, and `history/` (superseded runs) |
| [experiment-2-execution/](experiment-2-execution/) | 18 scored runs: `scores.csv`, `RESULTS.md`, readable `transcripts/`, `raw/` logs incl. final sandbox state, `inputs/` (tasks, answer keys, oracle decisions, agent prompts), `graph/` (playbooks and traces in Neo4j at the end), `development-runs/` |
| [experiment-3-banking/](experiment-3-banking/) | 84 graded runs on the commercial-bank scenario: `results.json/csv`, `report.md`, questions and SQL answer keys, raw `runs/` (summaries + full step logs), `runs-superseded/`, and the cross-layer Cypher query |
| [knowledge-layer/](knowledge-layer/) | Graph counts by label and relationship type; the YAML model for both versions |
| [figures/](figures/) | Screenshots from the demo app |
| [tools/](tools/) | The scripts that assembled this repository from the code repository (no scoring is recomputed) |

Local file paths and database hostnames were removed from all files. Nothing here contains credentials.

## 9. Versions

| | Experiment 1 | Experiment 2 |
|---|---|---|
| Code | `main` at `cd25fe8` | `execution-pattern` at `c42345a` |
| Runs | 2026-09-30 to 2026-10-02 (4 batches) | 2026-10-07, batch `20261007T1700` |
| Model | Claude Opus 5.5 on Azure AI Foundry, effort high, ≤ 25 turns | same |
| Graph | Neo4j Aura (conversation instance) | Neo4j Aura (separate execution instance) |
| Model usage | $21.63 for 84 runs (A $13.72, B $7.91) | $11.37 for 18 runs |
