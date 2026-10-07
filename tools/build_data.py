"""Assemble this repository's data folders from the demo repository's two working copies (read-only).

    python tools/build_data.py --main <path to main checkout> --exec <path to execution-pattern checkout> \
                               --exec-stamp 20261007T1700

Copies only what the reported numbers rest on (plus clearly labeled history and development runs), writes one readable
transcript per run, and scrubs local paths and instance hostnames from every text file it writes. Nothing is
recomputed here: scores come from the demo's own result files.
"""

import argparse
import csv
import json
import re
import shutil
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
SCRUB = [(re.compile(r"/Users/[^\s\"']*?/(kl-demo-exec|kl-demo)/"), ""),
         (re.compile(r"/(private/)?tmp/[^\s\"']*"), "<tmp>"),
         (re.compile(r"[0-9a-f]{8}\.databases\.neo4j\.io"), "<aura-instance>"),
         (re.compile(r"/Users/[A-Za-z0-9._-]+"), "~")]


def scrub(text: str) -> str:
    for rx, rep in SCRUB:
        text = rx.sub(rep, text)
    return text


def put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(scrub(text))


def copy_text(src: Path, dst: Path) -> None:
    put(dst, src.read_text())


def short(v, n=500) -> str:
    s = v if isinstance(v, str) else json.dumps(v, default=str)
    s = s.replace("\n", " ")
    return s if len(s) <= n else s[:n] + " …"


def events(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]


# ------------------------------------------------------------------------------------------ experiment 1

def transcript_q(r: dict, ev: list[dict], summary: dict | None, question: dict) -> str:
    who = "A · warehouse tools only" if r["agent"] == "A" else "B · warehouse tools + Neo4j knowledge layer"
    j, g = r["judge"], r["governance"]
    L = [f"# {r['qid']} · {who} · {r['run_id']}", "",
         f"**Question:** {question['question']}  ", f"**Requester role:** {question.get('role')} · **category:** "
         f"{question.get('category')}  ",
         f"**Grade:** {j['verdict']} ({r['final_score']}) · {r['model_turns']} turns · {r['tool_calls']} tool calls · "
         f"{r['sql_queries']} SQL ({r['sql_errors']} errors) · ${r['cost_usd']} · {r['latency_s']} s  ",
         f"**Governance:** {g['checks']} warehouse calls checked · {g['allowed']} allowed · {g['masked']} masked · "
         f"{g['blocked']} blocked · {g['violation_calls']} violations", "",
         "## Grader (blind, against the answer key)", "", f"- Verdict: **{j['verdict']}** ({j['score']})",
         f"- Correct facts: {'; '.join(j.get('correct_facts') or []) or '—'}",
         f"- Missed or wrong: {'; '.join(j.get('missed_or_wrong') or []) or '—'}", f"- Rationale: {j['rationale']}", ""]
    if g["violations"]:
        L += ["**Policy violations found by the audit:** " + "; ".join(f"{v['policy']} {v['what']} ({v['table']})"
                                                                      for v in g["violations"]), ""]
    L += ["## Timeline", "", "Reasoning lines are the model's summarized thinking. Cypher is what the knowledge-layer "
          "tools ran on Neo4j (Agent B).", ""]
    for e in ev:
        t = e.get("type")
        if t == "model":
            L.append(f"### Turn {e['step']}")
            for th in e.get("reasoning") or []:
                L.append(f"> 💭 {short(th, 900)}")
            if e.get("text") and e.get("tool_calls"):
                L.append(f"> {short(e['text'], 400)}")
            L.append("")
        elif t == "policy_gate":
            L.append(f"- 🛡 policy gate: **{e.get('decision')}** {', '.join(e.get('policies') or [])} "
                     f"on {', '.join(x.split('.', 1)[-1] for x in e.get('tables') or [])}")
        elif t == "tool":
            inp = e.get("input") or {}
            tag = " ⚠️ error" if e.get("is_error") else ""
            if isinstance(inp, dict) and "sql" in inp:
                L += [f"- 🔧 `{e['tool']}` on {inp.get('platform')}{tag}", "", "  ```sql", "  " + inp["sql"].strip().replace("\n", "\n  "),
                      "  ```"]
            else:
                L.append(f"- 🔧 `{e['tool']}`{tag} {short(inp, 300)}")
            if e.get("cypher"):
                L.append(f"  - Cypher on Neo4j: {len(e['cypher'])} quer{'y' if len(e['cypher']) == 1 else 'ies'}, "
                         f"first: `{short(e['cypher'][0]['cypher'], 200)}`")
            if e.get("result_excerpt"):
                L.append(f"  - → {short(e['result_excerpt'], 350)}")
    answer = (summary or {}).get("answer") or next((e.get("answer") for e in ev if e.get("type") == "end"), "")
    L += ["", "## Final answer", "", answer or "(none)", ""]
    return "\n".join(L)


def experiment1(main: Path) -> dict:
    out = OUT / "experiment-1-conversation"
    if out.exists():
        shutil.rmtree(out)
    questions = {q["id"]: q for q in __import__("yaml").safe_load((main / "eval" / "questions.yaml").read_text())}
    results = json.loads((main / "eval" / "results.json").read_text())
    final_ids = set()
    rows = []
    for r in results:
        base = main / "runs" / r["run_id"]
        stem = f"{r['agent']}_{r['qid']}"
        final_ids.add((r["run_id"], stem))
        for ext in ("json", "jsonl"):
            if (base / f"{stem}.{ext}").exists():
                copy_text(base / f"{stem}.{ext}", out / "raw" / r["run_id"] / f"{stem}.{ext}")
        ev = events(base / f"{stem}.jsonl")
        summary = json.loads((base / f"{stem}.json").read_text()) if (base / f"{stem}.json").exists() else None
        rep = r["run_id"].rsplit("_", 1)[-1]
        tpath = f"transcripts/{r['qid']}/{r['agent']}_{rep}_{r['run_id'].split('_')[1]}.md"
        put(out / tpath, transcript_q(r, ev, summary, questions[r["qid"]]))
        g = r["governance"]
        rows.append({"question": r["qid"], "category": questions[r["qid"]].get("category"), "agent": r["agent"],
                     "run_id": r["run_id"], "score": r["final_score"], "verdict": r["judge"]["verdict"],
                     "governance_violations": len(g["violations"]), "warehouse_calls_checked": g["checks"],
                     "blocked": g["blocked"], "model_turns": r["model_turns"], "tool_calls": r["tool_calls"],
                     "sql_queries": r["sql_queries"], "sql_errors": r["sql_errors"], "cost_usd": r["cost_usd"],
                     "latency_s": r["latency_s"], "transcript": tpath, "raw": f"raw/{r['run_id']}/{r['agent']}_{r['qid']}.jsonl"})
    rows.sort(key=lambda x: (int(x["question"][1:]), x["agent"], x["run_id"]))
    with open(out / "scores.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    copy_text(main / "eval" / "results.json", out / "results.json")
    # inputs
    for f in ("questions.yaml", "golden_answers.json", "question_renumbering.json", "questions_removed.yaml"):
        if (main / "eval" / f).exists():
            copy_text(main / "eval" / f, out / "inputs" / f)
    src = (main / "eval" / "scoring.py").read_text()
    prompt = re.search(r'JUDGE_PROMPT = """(.*?)"""', src, re.S).group(1)
    put(out / "inputs" / "grader_prompt.md", "# Grader prompt (blind: question, check rule, answer key, final answer)\n\n"
        "```text\n" + prompt.strip() + "\n```\n\nSource: `eval/scoring.py` on the code repository's main branch.\n")
    put(out / "inputs" / "agent_prompts.py", (main / "agents" / "prompts.py").read_text())
    for f in ("report.md", "WALKTHROUGH.md", "GOLDEN.md"):
        if (main / "eval" / f).exists():
            copy_text(main / "eval" / f, out / "original-reports" / f)
    # history: earlier iterations and the removed question
    hist = out / "history"
    for f, label in (("results_before_kl_fixes.json", "before-kl-fixes"), ("results_v1_kl_lookup_tools.json",
                                                                           "v1-kl-lookup-tools")):
        old = json.loads((main / "eval" / f).read_text())
        copy_text(main / "eval" / f, hist / label / "results.json")
        n = 0
        for r in old:
            stem = f"{r['agent']}_{r['qid']}"
            if (r["run_id"], stem) in final_ids:
                continue
            for ext in ("json", "jsonl"):
                p = main / "runs" / r["run_id"] / f"{stem}.{ext}"
                if p.exists() and not (hist / "raw" / r["run_id"] / f"{stem}.{ext}").exists():
                    copy_text(p, hist / "raw" / r["run_id"] / f"{stem}.{ext}")
                    n += ext == "jsonl"
        print(f"history {label}: {n} superseded runs copied")
    removed = main / "runs" / "_removed_Q3"
    if removed.exists():
        for p in removed.rglob("*"):
            if p.is_file() and p.suffix in (".json", ".jsonl"):
                copy_text(p, hist / "removed-question" / p.relative_to(removed))
    print(f"experiment 1: {len(rows)} scored runs")
    return {"runs": len(rows)}


# ------------------------------------------------------------------------------------------ experiment 2

DEV_RUNS = {
    "execution_dry1": "First end-to-end run of Agent B on T1 (before the approval threshold change).",
    "execution_dry2": "A on T1; B on T2, T3, T6, T7, T8. Found that the first T6/T7 scenario was wrong (the materials "
                      "were used at one plant only, so the backup supplier covered everything).",
    "execution_dry3": "A and B on the corrected T6, then B on T7. B treated the partial approval as covered (no discovery).",
    "execution_dry4": "B on T6 → review → T7 after the process branch conditions were made precise: first full learning loop.",
    "execution_dry5": "B on T1 after the approval threshold changed to $25,000 per DC plan: verifies approval before writing.",
}


def experiment2(exec_root: Path, stamp: str) -> dict:
    out = OUT / "experiment-2-execution"
    if out.exists():
        shutil.rmtree(out)
    pkg = exec_root / "results" / "execution" / stamp
    for p in pkg.rglob("*"):
        if p.is_file():
            dst = out / p.relative_to(pkg)
            if p.suffix in (".md", ".json", ".jsonl", ".csv", ".yaml", ".txt"):
                copy_text(p, dst)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(p, dst)
    dev = out / "development-runs"
    lines = ["# Development runs (not part of the reported results)", "",
             "Single runs made while building the benchmark. They are kept because they show how the task set and the "
             "process model were corrected before the reported runs. Earlier code versions; numbers here are not results.",
             "", "| Folder | What it was for |", "|---|---|"]
    for name, why in DEV_RUNS.items():
        src = exec_root / "runs" / name
        if not src.exists():
            continue
        for p in src.iterdir():
            if p.suffix in (".json", ".jsonl"):
                copy_text(p, dev / name / p.name)
        lines.append(f"| `{name}/` | {why} |")
    put(dev / "README.md", "\n".join(lines) + "\n")
    for f in ("prompts.py",):
        put(out / "inputs" / f"agent_{f}", (exec_root / "agents" / f).read_text())
    print("experiment 2 packaged")
    return {}


# ------------------------------------------------------------------------------------------ knowledge layer

def knowledge_layer(main: Path, exec_root: Path) -> None:
    out = OUT / "knowledge-layer" / "model"
    if out.exists():
        shutil.rmtree(out)
    for label, root in (("conversation", main), ("execution", exec_root)):
        for p in sorted((root / "kl" / "ontology").glob("*.yaml")) + [root / "kl" / "osi" / "semantic_model.yaml"]:
            copy_text(p, out / label / p.name)
    print("knowledge-layer model copied")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", required=True, type=Path)
    ap.add_argument("--exec", required=True, type=Path)
    ap.add_argument("--exec-stamp", required=True)
    ap.add_argument("--only", default="1,2,kl")
    a = ap.parse_args()
    parts = a.only.split(",")
    if "1" in parts:
        experiment1(a.main)
    if "2" in parts:
        experiment2(a.exec, a.exec_stamp)
    if "kl" in parts:
        knowledge_layer(a.main, a.exec)


if __name__ == "__main__":
    main()
