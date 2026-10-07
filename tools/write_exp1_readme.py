"""Write experiment-1-conversation/README.md; every number is read from scores.csv and inputs/questions.yaml."""

import csv
import statistics as st
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
E1 = ROOT / "experiment-1-conversation"
rows = list(csv.DictReader(open(E1 / "scores.csv")))
qs = {q["id"]: q for q in yaml.safe_load((E1 / "inputs" / "questions.yaml").read_text())}


def mean(xs, nd=2):
    return round(st.mean(xs), nd)


by_q = defaultdict(lambda: defaultdict(list))
for r in rows:
    by_q[r["question"]][r["agent"]].append(r)

tot = {a: [r for r in rows if r["agent"] == a] for a in "AB"}
L = ["# Experiment 1 · Conversation: answering business questions", "",
     "**Question.** With the same model, the same data and the same SQL tools, does giving an agent a Neo4j knowledge layer "
     "change how well it answers business questions that span two data platforms?", "",
     "**Setup.** 14 business questions × 3 replicates × 2 agents = 84 runs. Agent A has warehouse tools only "
     "(list tables, describe a table, run read-only SQL on Snowflake and Fabric). Agent B has the same tools plus five "
     "knowledge-layer tools (one context traversal, supply-network traversal, lead times, governed reference data, policy "
     "check). The harness checks data-use policy before every warehouse call B makes, and writes a decision trace after "
     "every B answer. A is audited afterwards against the same policies. Same model (Claude Opus 5.5), effort (high), "
     "prompt skeleton and turn cap (25) for both. B's prompt adds one paragraph about the knowledge layer "
     "([inputs/agent_prompts.py](inputs/agent_prompts.py)).", "",
     "**Scoring.** A blind LLM grader compares each final answer with an answer key computed by SQL from the warehouses "
     "([inputs/golden_answers.json](inputs/golden_answers.json), prompt in [inputs/grader_prompt.md](inputs/grader_prompt.md)): "
     "1 correct, 0.5 partial, 0 incorrect. Governance is scored separately: every warehouse call is checked against the "
     "layer's data-use policies; a violation is a call a policy denies, or a result that exposed a masked column.", "",
     "## Results", "",
     "| | Agent A (warehouse only) | Agent B (+ knowledge layer) |", "|---|---|---|",
     f"| Mean grade | {mean([float(r['score']) for r in tot['A']])} | {mean([float(r['score']) for r in tot['B']])} |",
     f"| Runs with a governance violation | {sum(int(r['governance_violations']) > 0 for r in tot['A'])} of {len(tot['A'])} | "
     f"{sum(int(r['governance_violations']) > 0 for r in tot['B'])} of {len(tot['B'])} |",
     f"| Mean cost per run | ${mean([float(r['cost_usd']) for r in tot['A']], 3)} | ${mean([float(r['cost_usd']) for r in tot['B']], 3)} |",
     f"| Total cost (42 runs) | ${sum(float(r['cost_usd']) for r in tot['A']):.2f} | ${sum(float(r['cost_usd']) for r in tot['B']):.2f} |",
     f"| Mean time per run | {mean([float(r['latency_s']) for r in tot['A']], 0):.0f} s | {mean([float(r['latency_s']) for r in tot['B']], 0):.0f} s |",
     f"| Mean model turns | {mean([int(r['model_turns']) for r in tot['A']], 1)} | {mean([int(r['model_turns']) for r in tot['B']], 1)} |",
     f"| Mean tool calls | {mean([int(r['tool_calls']) for r in tot['A']], 1)} | {mean([int(r['tool_calls']) for r in tot['B']], 1)} |",
     f"| SQL errors (all runs) | {sum(int(r['sql_errors']) for r in tot['A'])} | {sum(int(r['sql_errors']) for r in tot['B'])} |", "",
     "## By question", "",
     "Grades are means over 3 runs. Click a grade to open the first replicate's transcript.", "",
     "| Q | Category | Question | A grade | B grade | A $ | B $ | A s | B s |", "|---|---|---|---|---|---|---|---|---|"]
for qid in sorted(by_q, key=lambda q: int(q[1:])):
    a, b = by_q[qid]["A"], by_q[qid]["B"]
    L.append(f"| {qid} | {qs[qid].get('category')} | {qs[qid]['question']} | "
             f"[{mean([float(r['score']) for r in a])}]({a[0]['transcript']}) | [{mean([float(r['score']) for r in b])}]({b[0]['transcript']}) | "
             f"{mean([float(r['cost_usd']) for r in a])} | {mean([float(r['cost_usd']) for r in b])} | "
             f"{mean([float(r['latency_s']) for r in a], 0):.0f} | {mean([float(r['latency_s']) for r in b], 0):.0f} |")
L += ["", "## How the runs were assembled", "",
      "The 84 scored runs come from four batch runs (folder names `eval_<date>T<time>_r<replicate>`). After the first full "
      "batch, some knowledge-layer issues were fixed and the affected questions were re-run for both agents in later "
      "batches; one question (originally Q3) was removed and the rest renumbered. `scores.csv` lists the exact run behind "
      "each score. Everything that was superseded is kept in [history/](history/):", "",
      "- `history/before-kl-fixes/`: the first full batch's scores, before the knowledge-layer fixes.",
      "- `history/v1-kl-lookup-tools/`: scores of the first version of Agent B, which used many small lookup tools instead "
      "of one context traversal.",
      "- `history/raw/`: the raw logs of runs that were later replaced.",
      "- `history/removed-question/`: runs of the question that was dropped.", "",
      "Question ids everywhere use the current numbering ([inputs/question_renumbering.json](inputs/question_renumbering.json)).", "",
      "## Files", "",
      "| Path | What it is |", "|---|---|",
      "| `scores.csv` | One row per scored run: grade, governance, turns, tool calls, SQL, cost, time, links to transcript and raw log |",
      "| `transcripts/Qn/<agent>_<replicate>_<batch>.md` | Readable run: grader verdict and rationale, reasoning summaries, every SQL and knowledge-layer call (with the Cypher it ran), policy-gate decisions, final answer |",
      "| `raw/<run_id>/<agent>_<Q>.jsonl` / `.json` | The exact event log and run summary the numbers come from |",
      "| `results.json` | Full grader and governance output per run |",
      "| `inputs/` | Questions, answer keys with the SQL that produced them, grader prompt, agent prompts |",
      "| `original-reports/` | The reports generated in the code repository at the time (report, walkthrough, answer-key notes) |",
      "| `history/` | Superseded scores and runs (see above) |", ""]
(E1 / "README.md").write_text("\n".join(L))
print("wrote", E1 / "README.md")
