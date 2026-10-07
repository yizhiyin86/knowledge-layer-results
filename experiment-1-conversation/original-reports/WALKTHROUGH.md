# Evaluation walkthrough: Agent A (warehouses only) vs Agent B (with the Neo4j knowledge layer)

84 scored runs: 14 questions × 3 runs × 2 agents. Same model (Claude Opus 5.5, effort high), same SQL tools, same warehouses. B also gets the Neo4j knowledge layer: graph tools that run Cypher, plus an automatic policy check (also Cypher) in front of every SQL query. Each question below shows one representative run (run 1); the numbers in tables are means over the 3 runs.

- **Accuracy** is the judge's grade against the SQL answer key (1 correct, 0.5 partial, 0 incorrect), nothing else.
- **Governance** is audited for both agents the same way: every warehouse call is checked against the knowledge layer's data-use policies (same role and purpose). For B that is what its policy gate decided at run time; for A it is what the knowledge layer would have decided. A violation is a call that ran although a policy denies it, or that returned columns a policy masks (patient keys).
- **SQL** = queries against Snowflake or Fabric. **Cypher** = queries the knowledge-layer tools ran on Neo4j.
- **Policy-gate Cypher** is counted separately: it runs automatically before each of B's SQL queries, not by the agent's choice.
- Cypher for recorded runs was captured by replaying B's graph tool calls with the same inputs (`python -m eval.capture_cypher`); new runs record it live.

## Contents

0. [How the metrics are calculated](#how-the-metrics-are-calculated)
1. [Cost and query rundown](#cost-and-query-rundown-all-questions)
2. [Making B cheaper: one traversal instead of many lookups](#making-b-cheaper-one-traversal-instead-of-many-lookups)
3. [Question by question](#question-by-question)

## How the metrics are calculated

| Metric | How it is measured |
|---|---|
| **Runs** | 14 questions × 3 runs per agent (42 each). Same model (Claude Opus 5.5 via Azure Foundry, effort high), same base prompt, same warehouse tools (list tables, describe table, read-only SQL capped at 200 rows and 60 s). B also has the knowledge-layer tools. Memory is cleared before each run set so B starts cold. |
| **Accuracy** | Each final answer is graded against an answer key computed by hand-written SQL on the live warehouses (`eval/golden.py`), with a per-question check rule and tolerances. The grader (Claude, effort low) does not know which agent wrote the answer: 1 correct, 0.5 partial, 0 incorrect. Reported as the mean over runs and questions. Nothing else changes the score. |
| **Cost** | Claude tokens reported by the API for every model call in the run, priced at Foundry list price for Opus 5.5: input $4, output $20 (includes thinking), cache read $0.20, cache write $5 per million tokens (prompt caching is on for both agents). Excludes warehouse compute, Neo4j, embeddings and the grader. |
| **Time** | Wall-clock from the question to the final answer: model calls, SQL and graph calls. Four runs execute in parallel. |
| **Model turns** | Number of model calls in the agent loop (each turn re-reads the conversation and may call tools). |
| **Tool calls** | Tool invocations by the agent (the harness's memory write is not counted). |
| **SQL queries** | `run_sql` calls against Snowflake or Fabric. Failed = the warehouse returned an error or the 60 s timeout hit. |
| **Cypher queries** | Every query the knowledge-layer server sent to Neo4j, captured at the Neo4j driver, including the automatic policy check in front of each warehouse call. |
| **Governance violation** | Every warehouse call (describe or SQL) of either agent is checked against the knowledge layer's data-use policies, with the role and purpose of the request. A violation is a call that ran although a policy denies it, or that returned columns a policy masks (patient keys). B is checked at run time by its policy gate; A is audited after the fact with the same policies. |
| **SQL purpose** | Each query labelled by Claude (effort low) as explore, join keys, answer, verify or retry; approximate, applied the same way to both agents (`eval/sql_purpose.py`). |

## Cost and query rundown, all questions

Means per run (3 runs per question). Cost is Claude tokens at Foundry list price ($4 / $20 per MTok in/out, cache read $0.20, cache write $5); warehouse and Neo4j compute are not included.

| Q | Score A | Score B | Cost A $ | Cost B $ | Time A s | Time B s | SQL A (fail) | SQL B (fail) | Cypher B (+ gate) | Graph calls B | Tokens in A / B (k) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | 1.00 | 1.00 | 0.24 | 0.19 | 131 | 71 | 10.0 (0) | 5.0 (2) | 6 (+5) | 2.0 | 94 / 68 |
| Q2 | 1.00 | 1.00 | 0.31 | 0.25 | 156 | 111 | 16.7 (0) | 9.3 (0) | 6 (+10) | 1.7 | 138 / 117 |
| Q3 | 1.00 | 1.00 | 0.22 | 0.13 | 124 | 52 | 10.7 (1) | 3.3 (0) | 5 (+3) | 1.0 | 80 / 32 |
| Q4 | 1.00 | 1.00 | 0.30 | 0.15 | 168 | 54 | 11.7 (0) | 3.0 (0) | 5 (+4) | 1.0 | 151 / 38 |
| Q5 | 1.00 | 1.00 | 0.19 | 0.13 | 101 | 54 | 9.7 (0) | 2.7 (0) | 5 (+3) | 1.0 | 80 / 37 |
| Q6 | 0.67 | 1.00 | 0.59 | 0.21 | 246 | 99 | 23.7 (6) | 5.3 (2) | 8 (+7) | 4.3 | 385 / 94 |
| Q7 | 1.00 | 1.00 | 0.45 | 0.33 | 170 | 99 | 15.0 (3) | 8.0 (1) | 9 (+10) | 5.0 | 274 / 177 |
| Q8 | 0.50 | 1.00 | 0.14 | 0.08 | 84 | 20 | 5.3 (2) | 0.0 (0) | 5 (+0) | 1.0 | 57 / 13 |
| Q9 | 0.50 | 1.00 | 0.34 | 0.10 | 187 | 38 | 13.3 (1) | 2.0 (0) | 5 (+2) | 1.0 | 188 / 25 |
| Q10 | 1.00 | 1.00 | 0.39 | 0.24 | 151 | 78 | 16.0 (5) | 4.7 (0) | 7 (+6) | 3.0 | 202 / 102 |
| Q11 | 1.00 | 1.00 | 0.30 | 0.13 | 111 | 40 | 13.0 (4) | 3.0 (0) | 7 (+3) | 2.7 | 147 / 36 |
| Q12 | 0.33 | 1.00 | 0.52 | 0.36 | 183 | 111 | 19.3 (3) | 5.3 (0) | 13 (+6) | 7.3 | 326 / 148 |
| Q13 | 0.00 | 1.00 | 0.32 | 0.20 | 169 | 71 | 11.7 (0) | 2.0 (0) | 9 (+2) | 2.7 | 176 / 55 |
| Q14 | 0.50 | 1.00 | 0.26 | 0.12 | 93 | 37 | 9.7 (3) | 3.0 (1) | 6 (+3) | 1.7 | 111 / 43 |
| **All** | **0.75** | **1.00** | **13.72** total | **7.91** total | 148 | 67 | 557 (28) total | 170 (6) total | 479 total | 2.5 | 172 / 70 |

Fail = SQL that returned an error or hit the 60 s timeout (timeouts: A 0, B 0).

| Totals over the evaluation | A · without Neo4j | B · with Neo4j |
|---|---|---|
| Mean score | 0.75 | 1.00 |
| Claude cost (42 runs each) | $13.72 | $7.91 |
| Mean time per answer | 148 s | 67 s |
| Mean model turns | 11.3 | 5.4 |
| Mean tool calls | 23.5 | 7.1 |
| SQL queries (total / failed / timed out) | 557 / 28 / 0 | 170 / 6 / 0 |
| Cypher queries on Neo4j (total, incl. policy gate) | 0 | 479 |
| Mean input / output tokens per answer | 172k / 8.6k | 70k / 4.7k |
| Warehouse calls audited against policy | 920 | 193 |
| Calls blocked by the policy gate | n/a (no gate) | 0 |
| Governance violations (calls / runs) | 28 / 13 | 0 / 0 |
| Questions with a violation in any run | 5 / 14 | 0 / 14 |

Spend outside this evaluation (development and smoke runs, earlier eval rounds) is not in these totals; see KL_DEMO_STATUS.md.

## Making B cheaper: one traversal instead of many lookups

The first version of B had 25 knowledge-layer tools (neocarta's catalog tools plus 15 kl-ext lookups). The model assembled its context one layer at a time (concept, metric, data product, join path, rules, deprecated tables, policy, memory), each lookup taking 2–4 Cypher queries. The current B starts with **one `get_context` call**: vector search finds the entry points (concepts, metrics, rules, join paths, past answers) and one traversal expands across the layers to the authoritative tables, columns, join paths, rules, deprecated tables and the policies for this role and purpose. The supply-network traversal is one query instead of six, the policy check one query instead of two per table, and B no longer repeats its answer into a memory tool (the harness writes the decision trace). A is unchanged.

| Agent B, 42 runs | Before: lookup tools | Now: one context traversal |
|---|---|---|
| Mean score | 0.99 | 1.00 |
| Claude cost (total) | $12.40 | $7.91 |
| Mean time per answer | 111 s | 67 s |
| Mean model turns | 10.2 | 5.4 |
| Mean graph tool calls | 11.6 | 2.5 |
| Mean Cypher per answer (tools + policy gate) | 62 | 11 |
| SQL queries (total / failed) | 180 / 11 | 170 / 6 |
| Mean output tokens per answer | 7.1k | 4.7k |

## Question by question

### Q1 · parity · A 1.00 vs B 1.00

> What is Lacrivia's market share by payer channel over the last 13 weeks, and how is it trending?  
> requester role: `MARKET_ACCESS`

**Outcome:** Both agents got the right channel shares and trends (Commercial up, Medicare Part D down). B got there with a shorter, more direct path because the graph supplied the market definition up front.

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Listed Snowflake tables, then described seven of them, including two candidate marts (MART.PYR_SHR_WK and MART.PYR_SHR_WK_OLD), RAW_3P.RXT_WKLY, BIZ.MKT_DEF_DRIVER and CORE.PAYER_SPINE.</li><li>Ran data-quality probes on the raw TRx feed (unmatched plans, channel mismatches, duplicates, negative quantities) and compared the mart with a recomputation from raw TRx joined to the DRY_EYE driver.</li><li>Computed 13-week, prior-13-week and first-4 vs last-4-week shares from MART.PYR_SHR_WK, for example Commercial 26.2% (23.6%→28.8%) and Part D 19.8% (22.3%→18.3%), and added competitor context.</li><li>Used 11 SQL queries in total. Graded correct.</li></ul></td>
<td valign='top'><ul><li>A single get_context call (3 Cypher queries) returned the Channel concept, candidate tables and policy checks. get_reference then returned the 12-pack DRY_EYE market definition straight from the graph.</li><li>Confirmed the market definition in Snowflake by joining CORE.PRODUCT to BIZ.MKT_DEF_DRIVER, and checked the available week range.</li><li>Computed share by channel directly from RAW_3P.RXT_WKLY joined to the effective-dated DRY_EYE driver for the last 13 weeks, plus a weekly breakdown. Results: Commercial 26.2%, Part D 19.8%, total 23.7%.</li><li>Logged the decision trace back to the graph. Used 4 SQL queries in total. Graded correct.</li></ul></td></tr>
<tr><td>Run 1: <b>11 SQL</b> (0 failed), 0 Cypher</td><td>Run 1: <b>4 SQL</b> (0 failed), <b>6 Cypher</b> from 2 graph calls (+4 policy-gate)</td></tr>
<tr><td>3-run mean: $0.24, 131 s, 18 tool calls</td><td>3-run mean: $0.19, 71 s, 7 tool calls</td></tr></table>

**Why the difference:** The numbers were identical. B's knowledge layer named the market definition and the relevant tables up front, so it skipped A's schema exploration, the choice between two mart tables, and the data-quality checks.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Snowflake → 7 rows<pre><code>with b as (select wk_end_dt, chnl_cd, brand_trx, mkt_trx, shr_pct, dense_rank() over (order by wk_end_dt desc) rk from PHARMA_DEMO.MART.PYR_SHR_WK where mkt_def=&#x27;DRY_EYE&#x27; and brand_nm=&#x27;LACRIVIA&#x27;)
select chnl_cd,
 round(100*sum(iff(rk&lt;=13,brand_trx,0))/sum(iff(rk&lt;=13,mkt_trx,0)),2) shr_l13,
 round(100*sum(iff(rk between 14 and 26,brand_trx,0))/sum(iff(rk between 14 and 26,mkt_trx,0)),2) shr_p13,
 round(100*sum(iff(rk&lt;=4,brand_trx,0))/sum(iff(rk&lt;=4,mkt_trx,0)),2) shr_l4,
 round(100*sum(iff(rk between 10 and 13,brand_trx,0))/sum(iff(rk between 10 and 13,mkt_trx,0)),2) shr_first4_of_l13,
 sum(iff(rk&lt;=13,brand_trx,0)) lac_trx_l13, sum(iff(rk&lt;=13,mkt_trx,0)) mkt_trx_l13,
 sum(iff(rk between 14 and 26,brand_trx,0)) lac_trx_p13, sum(iff(rk between 14 and 26,mkt_trx,0)) mkt_trx_p13,
 round(regr_slope(iff(rk&lt;=13,shr_pct,null), iff(rk&lt;=13,14-rk,null)),3) slope_pp_per_wk
from b group by rollup(chnl_cd) order by 1</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · reference data → 12 rows<pre><code>MATCH (p:PackagedProduct)-[:IN_MARKET]-&gt;(m:TherapeuticMarket)
RETURN m.name AS market, p.brand AS brand, p.pack AS pack, p.ndc11 AS ndc11,
       p.company = &#x27;Y&#x27; AS company_product ORDER BY market, brand</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (11)</summary>

1. `SQL · snowflake` → 12 rows: `select p.*, d.mkt_def, d.eff_from, d.eff_to, d.src_file from PHARMA_DEMO.CORE.PRODUCT p full outer join PHARMA_DEMO.BIZ.MKT_DEF_DRIVER d on …`
2. `SQL · snowflake` → 6 rows: `select * from PHARMA_DEMO.REF.CHNL…`
3. `SQL · snowflake` → 6 rows: `select chnl_cd, count(*), min(wk_end_dt), max(wk_end_dt), count(distinct wk_end_dt), sum(trx_qty) from PHARMA_DEMO.RAW_3P.RXT_WKLY group by …`
4. `SQL · snowflake` → 12 rows: `select mkt_def, chnl_cd, count(distinct wk_end_dt) wks, min(wk_end_dt), max(wk_end_dt), count(distinct brand_nm) brands, listagg(distinct br…`
5. `SQL · snowflake` → 12 rows: `select r.prod_ndc11, p.brand_nm, count(*), sum(trx_qty), sum(case when r.plan_id is null then 1 else 0 end) null_plan, sum(case when s.plan_…`
6. `SQL · snowflake` → 1 rows: `select count(*) n, count(distinct wk_end_dt, prscrbr_me, prod_ndc11, plan_id, chnl_cd) nkey, count(distinct wk_end_dt, prscrbr_me, prod_ndc1…`
7. `SQL · snowflake` → 6 rows: `with raw as ( select r.wk_end_dt, r.chnl_cd, sum(iff(p.brand_nm='LACRIVIA',trx_qty,0)) brand_trx, sum(trx_qty) mkt_trx from PHARMA_DEMO.RAW_…`
8. `SQL · snowflake` → 22 rows: `select wk_end_dt, sum(iff(brand_nm='LACRIVIA',brand_trx,0)) lac, max(mkt_trx) mkt_c_dummy, sum(brand_trx) sum_brand_all_ch, count(*) rws fro…`
9. `SQL · snowflake` → 7 rows: `with b as (select wk_end_dt, chnl_cd, brand_trx, mkt_trx, shr_pct, dense_rank() over (order by wk_end_dt desc) rk from PHARMA_DEMO.MART.PYR_…`
10. `SQL · snowflake` → 13 rows: `select wk_end_dt, round(100*sum(iff(chnl_cd='C',brand_trx,0))/sum(iff(chnl_cd='C',mkt_trx,0)),1) c, round(100*sum(iff(chnl_cd='D',brand_trx,…`
11. `SQL · snowflake` → 12 rows: `with b as (select *, dense_rank() over (order by wk_end_dt desc) rk from PHARMA_DEMO.MART.PYR_SHR_WK where mkt_def='DRY_EYE' and chnl_cd in …`

</details>
<details><summary>All of B's queries in run 1 (10, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 18 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 0 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `Cypher · reference data` → 12 rows: `MATCH (p:PackagedProduct)-[:IN_MARKET]->(m:TherapeuticMarket) RETURN m.name AS market, p.brand AS brand, p.pack AS pack, p.ndc11 AS ndc11, p…`
5. `SQL · snowflake` → 12 rows: `SELECT p.*, m.MKT_DEF, m.EFF_FROM, m.EFF_TO FROM PHARMA_DEMO.CORE.PRODUCT p LEFT JOIN PHARMA_DEMO.BIZ.MKT_DEF_DRIVER m ON p.PROD_NDC11=m.PRO…`
6. `SQL · snowflake` → 1 rows: `SELECT MIN(WK_END_DT), MAX(WK_END_DT), COUNT(DISTINCT WK_END_DT) FROM PHARMA_DEMO.RAW_3P.RXT_WKLY…`
7. `SQL · snowflake` → 7 rows: `WITH wk AS (SELECT DISTINCT WK_END_DT FROM PHARMA_DEMO.RAW_3P.RXT_WKLY ORDER BY WK_END_DT DESC LIMIT 13), rx AS ( SELECT r.WK_END_DT, r.CHNL…`
8. `SQL · snowflake` → None rows: `WITH wk AS (SELECT DISTINCT WK_END_DT FROM PHARMA_DEMO.RAW_3P.RXT_WKLY ORDER BY WK_END_DT DESC LIMIT 13) SELECT r.WK_END_DT, r.CHNL_CD, ROUN…`
9. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
10. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>

### Q2 · definition · A 1.00 vs B 1.00

> Which company product had the highest claim rejection rate in the last 13 weeks, and what is driving the rejections?  
> requester role: `MARKET_ACCESS`

**Outcome:** Both agents correctly named LACRIVIA (18.5% rejection rate, prior authorization at 58% of rejections, Northstar Commercial as the top plan), so this question was a tie on correctness.

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Listed Snowflake tables and described RAW_3P.CLMLNS_ADJ, CORE.PRODUCT, REF.REJ_CODE, RXT_WKLY and PAYER_SPINE, then profiled adjudication statuses, NDC formats and reject codes on its own.</li><li>Worked out the 13-week window (27 Jun – 25 Sep 2026) from the weekly Rx table&#x27;s dates, then computed rates excluding reversals (query 8), giving LACRIVIA 2,367/12,809 = 18.5%.</li><li>Broke LACRIVIA&#x27;s rejections down by reject group, code, channel, payer and patient type, finding prior authorization at 58% (codes PA 500, 75 at 439, 3N at 433) and Northstar Commercial as the top plan.</li><li>The grader noted one slip: it gave Northstar&#x27;s 35% overall rejection rate rather than its 31.6% PA rate.</li></ul></td>
<td valign='top'><ul><li>A single get_context call ran graph Cypher that returned the ClaimRejection concept (reject codes rolled up to reject groups), matching tables and policy checks.</li><li>It then used SQL to confirm the date range and the 13-week window, and computed rates per pack with a ROLLUP using paid + rejected as the denominator (query 10): 18.5%, with the 10 mL pack at 20.6%.</li><li>It broke rejections down by reject group, plan, month, code and substitution, reporting PA at 58% and Northstar with a 35% rejection rate and 32% PA rate. Two of its SQL queries returned no rows.</li><li>It logged a DecisionTrace to the graph memory.</li></ul></td></tr>
<tr><td>Run 1: <b>15 SQL</b> (0 failed), 0 Cypher</td><td>Run 1: <b>13 SQL</b> (0 failed), <b>5 Cypher</b> from 1 graph calls (+14 policy-gate)</td></tr>
<tr><td>3-run mean: $0.31, 156 s, 23 tool calls</td><td>3-run mean: $0.25, 111 s, 12 tool calls</td></tr></table>

**Why the difference:** Both reached the same correct numbers. A had to discover the schema and the reject-group mapping itself. B got the concept and the reject-group structure from the graph up front, and it stated the PA rate for the top plan more precisely.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Snowflake → 10 rows<pre><code>select p.brand_nm, p.co_flg,
 sum(iff(adj_stat=&#x27;P&#x27;,1,0)) paid, sum(iff(adj_stat=&#x27;R&#x27;,1,0)) rej, sum(iff(adj_stat=&#x27;V&#x27;,1,0)) rev,
 round(rej/(paid+rej)*100,2) rej_rate_pct, round(rej/(paid+rej+rev)*100,2) rej_rate_incl_v
from PHARMA_DEMO.RAW_3P.CLMLNS_ADJ c join PHARMA_DEMO.CORE.PRODUCT p on p.prod_ndc11=c.prod_ndc11
where clm_dt between &#x27;2026-06-27&#x27; and &#x27;2026-09-25&#x27;
group by 1,2 order by co_flg desc, rej_rate_pct desc</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · context: one traversal across all layers → 1 rows<pre><code>CALL () { CALL db.index.vector.queryNodes(&#x27;concept_vector_index&#x27;, 5, $v) YIELD node, score WHERE score &gt; 0.55
          RETURN collect(node) AS concepts }
CALL () { CALL db.index.vector.queryNodes(&#x27;metric_vector_index&#x27;, 3, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS m0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;businessrule_vector_index&#x27;, 3, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS r0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;joinpath_vector_index&#x27;, 2, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS j0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;decisiontrace_vector_index&#x27;, 2, $v) YIELD node, score WHERE score &gt; 0.8
          RETURN collect({question: node.question, answer: left(node.answer, 1500), similarity: round(score, 3),
                          sql: COLLECT { MATCH (node)-[r:RAN]-&gt;(s:SqlStep) RETURN s.platform + &#x27;: &#x27; + s.sql ORDER BY r.order }})
                 AS past }
WITH concepts, m0, r0, j0, past,
     COLLECT { UNWIND concepts AS c MATCH (d:DataProduct)-[:REALIZES]-&gt;(c) RETURN DISTINCT d } AS dps
WITH concepts, past, dps,
     apoc.coll.toSet(COLLECT { UNWIND dps AS d MATCH (d)-[:INCLUDES]-&gt;(t:Table) RETURN t }
                     + COLLECT { UNWIND concepts AS c MATCH (c)-[:MAPPED_TO {role: &#x27;table&#x27;}]-&gt;(t:Table) RETURN t }) AS tabs,
     apoc.coll.toSet(m0 + COLLECT { UNWIND concepts AS c MATCH (m:Metric)-[:MEASURES]-&gt;(c) RETURN m }) AS mets,
     apoc.coll.toSet(r0 + COLLECT { UNWIND concepts AS c MATCH (b:BusinessRule)-[:ABOUT]-&gt;(c) RETURN b }) AS rules,
     apoc.coll.toSet(j0 + COLLECT { UNWIND concepts AS c MATCH (j:JoinPath)-[:FROM_CONCEPT|TO_CONCEPT]-&gt;(c) RETURN j }) AS jps,
     COLLECT { UNWIND concepts AS c MATCH (s:Step)-[:INVOLVES]-&gt;(c) RETURN DISTINCT s } AS steps
RETURN
  [c IN concepts | {concept: c.name, definition: c.definition,
     aligned_with: COLLECT { MATCH (c)-[:ALIGNED_WITH]-&gt;(s:StandardTerm) RETURN s.standard + &#x27;: &#x27; + s.term },
     related: COLLECT { MATCH (c)-[r]-(o:Concept) WHERE r.domain
                        RETURN DISTINCT startNode(r).name + &#x27; -&#x27; + type(r) + &#x27;-&gt; &#x27; + endNode(r).name }}] AS concepts,
  [d IN dps | {data_product: d.name, status: d.status, owner: COLLECT { MATCH (t:Team)-[:OWNS]-&gt;(d) RETURN t.name }}] AS data_products,
  [t IN tabs | {table: t.fq_name, platform: t.platform, status: t.status, description: left(t.description, 160),
     hits: size([c IN concepts WHERE EXISTS { (c)-[:MAPPED_TO]-&gt;(t) } OR EXISTS { (c)-[:MAPPED_TO]-&gt;(:Column)&lt;-[:HAS_COLUMN]-(t) }]),
     columns: COLLECT { MATCH (t)-[:HAS_COLUMN]-&gt;(c:Column) RETURN c.name + coalesce(&#x27;: &#x27; + left(c.description, 60), &#x27;&#x27;) }}] AS tables,
  [m IN mets | {metric: m.name, status: m.status, description: left(m.description, 200),
     expression: COLLECT { MATCH (m)-[:HAS_EXPRESSION]-&gt;(e:Expression) RETURN e.expression },
     computed_from: COLLECT { MATCH (m)-[:COMPUTED_FROM]-&gt;(c:Column)&lt;-[:HAS_COLUMN]-(t:Table) RETURN t.fq_name + &#x27;.&#x27; + c.name },
     used_in_reports: COLLECT { MATCH (m)-[:USED_IN]-&gt;(r:Report) RETURN r.name },
     variants: COLLECT { MATCH (m)-[:VARIANT_OF]-(v:Metric) RETURN v.name + &#x27; [&#x27; + coalesce(v.status, &#x27;&#x27;) + &#x27;]&#x27; }}] AS metrics,
  [j IN jps | {join_path: j.name, description: j.description, transform: j.transform, max_depth: j.max_depth,
     steps: COLLECT { MATCH (j)-[s:STEP]-&gt;(c:Column)&lt;-[:HAS_COLUMN]-(t:Table) RETURN t.fq_name + &#x27;.&#x27; + c.name ORDER BY s.order }}] AS join_paths,
  [b IN rules | {rule: b.id, name: b.name, text: b.text}] AS business_rules,
  [s IN steps | {process: s.process, step: s.name, order: s.order, description: s.description}] AS process_steps,
  COLLECT { MATCH (t:Table) WHERE t.status IN [&#x27;deprecated&#x27;, &#x27;sandbox&#x27;]
            RETURN {table: t.fq_name, status: t.status, use_instead: t.replaced_by} } AS deprecated_tables,
  past AS similar_past_answers</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (15)</summary>

1. `SQL · snowflake` → 12 rows: `select * from PHARMA_DEMO.CORE.PRODUCT…`
2. `SQL · snowflake` → 16 rows: `select * from PHARMA_DEMO.REF.REJ_CODE…`
3. `SQL · snowflake` → 3 rows: `select adj_stat, count(*), min(clm_dt), max(clm_dt), count(distinct clm_id), sum(iff(rej_rsn_cd is null,1,0)) from PHARMA_DEMO.RAW_3P.CLMLNS…`
4. `SQL · snowflake` → 36 rows: `select prod_ndc11, length(prod_ndc11) l, adj_stat, count(*) from PHARMA_DEMO.RAW_3P.CLMLNS_ADJ group by 1,2,3 order by 1,3…`
5. `SQL · snowflake` → 16 rows: `select rej_rsn_cd, '['||rej_rsn_cd||']' b, count(*) from PHARMA_DEMO.RAW_3P.CLMLNS_ADJ where adj_stat='R' group by 1,2 order by 3 desc…`
6. `SQL · snowflake` → 1 rows: `select max(wk_end_dt), count(distinct wk_end_dt), dayname(max(wk_end_dt)) from PHARMA_DEMO.RAW_3P.RXT_WKLY…`
7. `SQL · snowflake` → 26 rows: `select clm_dt, adj_stat, count(*) from PHARMA_DEMO.RAW_3P.CLMLNS_ADJ where clm_dt >= '2026-09-19' group by 1,2 order by 1,2…`
8. `SQL · snowflake` → 10 rows: `select p.brand_nm, p.co_flg, sum(iff(adj_stat='P',1,0)) paid, sum(iff(adj_stat='R',1,0)) rej, sum(iff(adj_stat='V',1,0)) rev, round(rej/(pai…`
9. `SQL · snowflake` → 15 rows: `select r.rej_grp, c.rej_rsn_cd, r.rej_desc, count(*) n, round(n/sum(n) over()*100,1) pct_of_rej, round(n/12809*100,2) pct_of_claims from PHA…`
10. `SQL · snowflake` → 6 rows: `select * from PHARMA_DEMO.REF.CHNL…`
11. `SQL · snowflake` → 6 rows: `select iff(clm_dt>='2026-06-27','L13W','Prior13W') per, p.brand_nm, count_if(adj_stat='R') rej, count_if(adj_stat in ('P','R')) tot, round(r…`
12. `SQL · snowflake` → 6 rows: `select s.chnl_cd, count_if(adj_stat='R') rej, count_if(adj_stat in ('P','R')) tot, round(rej/tot*100,1) rate, count_if(r.rej_grp='PRIOR_AUTH…`
13. `SQL · snowflake` → 16 rows: `select s.payer_nm, s.pbm_nm, count_if(adj_stat='R') rej, count_if(adj_stat in ('P','R')) tot, round(rej/tot*100,1) rate, count_if(r.rej_grp=…`
14. `SQL · snowflake` → 4 rows: `select c.prod_ndc11, pat_typ, count_if(adj_stat='R') rej, count_if(adj_stat in ('P','R')) tot, round(rej/tot*100,1) rate, count_if(r.rej_grp…`
15. `SQL · snowflake` → None rows: `select c.plan_id, s.plan_nm, s.pbm_nm, count_if(adj_stat='R') rej, count_if(adj_stat in ('P','R')) tot, round(rej/tot*100,1) rate, count_if(…`

</details>
<details><summary>All of B's queries in run 1 (18, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 21 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 0 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `SQL · snowflake` → 1 rows: `SELECT MIN(CLM_DT), MAX(CLM_DT), COUNT(*), COUNT(DISTINCT PROD_NDC11) FROM PHARMA_DEMO.RAW_3P.CLMLNS_ADJ…`
5. `SQL · snowflake` → 16 rows: `SELECT DATE_TRUNC('week', CLM_DT) wk, COUNT(*) n FROM PHARMA_DEMO.RAW_3P.CLMLNS_ADJ WHERE CLM_DT >= '2026-06-15' GROUP BY 1 ORDER BY 1…`
6. `SQL · snowflake` → 13 rows: `SELECT CLM_DT, COUNT(*) FROM PHARMA_DEMO.RAW_3P.CLMLNS_ADJ WHERE CLM_DT >= '2026-09-18' GROUP BY 1 ORDER BY 1…`
7. `SQL · snowflake` → 3 rows: `SELECT * FROM PHARMA_DEMO.RAW_3P.RXT_WKLY LIMIT 3…`
8. `SQL · snowflake` → 12 rows: `SELECT p.CO_FLG, p.BRAND_NM, p.PACK_DESC, c.PROD_NDC11, COUNT(*) n, SUM(IFF(ADJ_STAT='P',1,0)) paid, SUM(IFF(ADJ_STAT='R',1,0)) rej, SUM(IFF…`
9. `SQL · snowflake` → 14 rows: `SELECT DISTINCT WK_END_DT FROM PHARMA_DEMO.RAW_3P.RXT_WKLY ORDER BY 1 DESC LIMIT 14…`
10. `SQL · snowflake` → 9 rows: `SELECT p.BRAND_NM, p.PACK_DESC, c.PROD_NDC11, SUM(IFF(ADJ_STAT='P',1,0)) paid, SUM(IFF(ADJ_STAT='R',1,0)) rej, ROUND(SUM(IFF(ADJ_STAT='R',1,…`
11. `SQL · snowflake` → 32 rows: `SELECT p.BRAND_NM, p.PACK_DESC, r.REJ_GRP, SUM(IFF(ADJ_STAT='R',1,0)) rej, ROUND(SUM(IFF(ADJ_STAT='R',1,0))/NULLIF(MAX(t.adj),0),4) grp_rate…`
12. `SQL · snowflake` → None rows: `SELECT s.PAYER_NM, s.PLAN_NM, s.PBM_NM, s.CHNL_CD, SUM(IFF(ADJ_STAT IN ('P','R'),1,0)) adj, SUM(IFF(ADJ_STAT='R',1,0)) rej, SUM(IFF(ADJ_STAT…`
13. `SQL · snowflake` → 24 rows: `SELECT DATE_TRUNC('month', CLM_DT) mth, p.PACK_DESC, SUM(IFF(ADJ_STAT IN ('P','R'),1,0)) adj, SUM(IFF(ADJ_STAT='R',1,0)) rej, SUM(IFF(ADJ_ST…`
14. `SQL · snowflake` → None rows: `SELECT p.PACK_DESC, c.REJ_RSN_CD, r.REJ_DESC, r.REJ_GRP, COUNT(*) rej, SUM(IFF(ABNDN_FLG='Y',1,0)) abandoned, SUM(IFF(SUBST_NDC11 IS NOT NUL…`
15. `SQL · snowflake` → 12 rows: `SELECT s.PLAN_NM, r.REJ_GRP, COUNT(*) rej FROM PHARMA_DEMO.RAW_3P.CLMLNS_ADJ c JOIN PHARMA_DEMO.CORE.PRODUCT p ON p.PROD_NDC11=c.PROD_NDC11 …`
16. `SQL · snowflake` → 5 rows: `SELECT COALESCE(sp.BRAND_NM,'(none)') subst_brand, sp.CO_FLG, COUNT(*) n, SUM(IFF(ABNDN_FLG='Y',1,0)) abandoned FROM PHARMA_DEMO.RAW_3P.CLML…`
17. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
18. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>

### Q3 · parity · A 1.00 vs B 1.00

> In district D-03, what is each rep's Lacrivia TRx attainment versus their IC goal quarter-to-date?  
> requester role: `FIELD_SALES`

**Outcome:** Both agents got every rep's attainment right (62.4% to 98.6%, with R017 and R022 under 70%), but Agent B got there in 3 SQL queries after one graph lookup, while Agent A explored with 11 queries and had to guess the crediting rule.

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Listed Snowflake tables and described 7 of them (IC_GOAL, REP_ROSTER, TERRITORY, RXT_WKLY, PRODUCT, PRESCRIBER, CALL_PLAN) to piece together the schema.</li><li>Profiled the data before computing anything: goal quarters, week coverage, NDC lengths and negative quantities, duplicate rows, call-plan alignment and the market-definition driver file.</li><li>Found no crediting-rules table, so it assumed both reps in a territory get full credit for that territory&#x27;s TRx and asked the user to confirm. That gave a credited total of 4,398 against 2,199 unique TRx.</li><li>Query 10 joined RXT_WKLY to PRODUCT (LACRIVIA) and PRESCRIBER by territory, then to the reps&#x27; goals, using 13 of 13 elapsed weeks. The grader marked every figure correct.</li></ul></td>
<td valign='top'><ul><li>One get_context call ran 3 Cypher queries. They returned the IncentiveGoal concept, the ratified ic_attainment metric (QTD territory TRx ÷ quarterly goal × elapsed weeks/13), the trusted tables and the applicable policies.</li><li>Pulled the D-03 roster and goals from REP_ROSTER joined to IC_GOAL, then checked week coverage in RXT_WKLY: 13 elapsed weeks, data through 25 Sep.</li><li>Computed attainment in a single SQL query that applied the metric definition directly. It cited the Finance metric and pointed out the high goals for the two Dorsey reps.</li><li>Logged a decision trace back to the graph.</li></ul></td></tr>
<tr><td>Run 1: <b>11 SQL</b> (0 failed), 0 Cypher</td><td>Run 1: <b>3 SQL</b> (0 failed), <b>5 Cypher</b> from 1 graph calls (+3 policy-gate)</td></tr>
<tr><td>3-run mean: $0.22, 124 s, 19 tool calls</td><td>3-run mean: $0.13, 52 s, 4 tool calls</td></tr></table>

**Why the difference:** Both reached the same correct numbers. Agent B had the metric definition, including the pro-rating, from the graph up front, so it needed fewer queries and could cite a ratified source. Agent A had to infer the logic by profiling the data and flag its crediting assumption for confirmation.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Snowflake → 9 rows<pre><code>with rx as (
 select p.terr_id, r.prscrbr_me, sum(r.trx_qty) trx
 from PHARMA_DEMO.RAW_3P.RXT_WKLY r join PHARMA_DEMO.CORE.PRODUCT pr on pr.prod_ndc11=r.prod_ndc11 and pr.brand_nm=&#x27;LACRIVIA&#x27;
 join PHARMA_DEMO.CORE.PRESCRIBER p on p.prscrbr_me=r.prscrbr_me
 where r.wk_end_dt between &#x27;2026-07-01&#x27; and &#x27;2026-09-30&#x27;
 group by 1,2)
select ro.rep_id, ro.rep_nm, ro.terr_id, ro.team, g.trx_goal,
 (select sum(trx) from rx where rx.terr_id=ro.terr_id) terr_trx,
 (select sum(trx) from rx join PHARMA_DEMO.CORE.CALL_PLAN cp on cp.prscrbr_me=rx.prscrbr_me and cp.rep_id=ro.rep_id and cp.fqtr=&#x27;2026Q3&#x27;) callplan_trx
from PHARMA_DEMO.CORE.REP_ROSTER ro left join PHARMA_DEMO.CORE.IC_GOAL g on g.rep_id=ro.rep_id and g.fqtr=&#x27;2026Q3&#x27; and g.brand_nm=&#x27;LACRIVIA&#x27;
where ro.district_id=&#x27;D-03&#x27; order by 1</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · context: one traversal across all layers → 1 rows<pre><code>CALL () { CALL db.index.vector.queryNodes(&#x27;concept_vector_index&#x27;, 5, $v) YIELD node, score WHERE score &gt; 0.55
          RETURN collect(node) AS concepts }
CALL () { CALL db.index.vector.queryNodes(&#x27;metric_vector_index&#x27;, 3, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS m0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;businessrule_vector_index&#x27;, 3, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS r0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;joinpath_vector_index&#x27;, 2, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS j0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;decisiontrace_vector_index&#x27;, 2, $v) YIELD node, score WHERE score &gt; 0.8
          RETURN collect({question: node.question, answer: left(node.answer, 1500), similarity: round(score, 3),
                          sql: COLLECT { MATCH (node)-[r:RAN]-&gt;(s:SqlStep) RETURN s.platform + &#x27;: &#x27; + s.sql ORDER BY r.order }})
                 AS past }
WITH concepts, m0, r0, j0, past,
     COLLECT { UNWIND concepts AS c MATCH (d:DataProduct)-[:REALIZES]-&gt;(c) RETURN DISTINCT d } AS dps
WITH concepts, past, dps,
     apoc.coll.toSet(COLLECT { UNWIND dps AS d MATCH (d)-[:INCLUDES]-&gt;(t:Table) RETURN t }
                     + COLLECT { UNWIND concepts AS c MATCH (c)-[:MAPPED_TO {role: &#x27;table&#x27;}]-&gt;(t:Table) RETURN t }) AS tabs,
     apoc.coll.toSet(m0 + COLLECT { UNWIND concepts AS c MATCH (m:Metric)-[:MEASURES]-&gt;(c) RETURN m }) AS mets,
     apoc.coll.toSet(r0 + COLLECT { UNWIND concepts AS c MATCH (b:BusinessRule)-[:ABOUT]-&gt;(c) RETURN b }) AS rules,
     apoc.coll.toSet(j0 + COLLECT { UNWIND concepts AS c MATCH (j:JoinPath)-[:FROM_CONCEPT|TO_CONCEPT]-&gt;(c) RETURN j }) AS jps,
     COLLECT { UNWIND concepts AS c MATCH (s:Step)-[:INVOLVES]-&gt;(c) RETURN DISTINCT s } AS steps
RETURN
  [c IN concepts | {concept: c.name, definition: c.definition,
     aligned_with: COLLECT { MATCH (c)-[:ALIGNED_WITH]-&gt;(s:StandardTerm) RETURN s.standard + &#x27;: &#x27; + s.term },
     related: COLLECT { MATCH (c)-[r]-(o:Concept) WHERE r.domain
                        RETURN DISTINCT startNode(r).name + &#x27; -&#x27; + type(r) + &#x27;-&gt; &#x27; + endNode(r).name }}] AS concepts,
  [d IN dps | {data_product: d.name, status: d.status, owner: COLLECT { MATCH (t:Team)-[:OWNS]-&gt;(d) RETURN t.name }}] AS data_products,
  [t IN tabs | {table: t.fq_name, platform: t.platform, status: t.status, description: left(t.description, 160),
     hits: size([c IN concepts WHERE EXISTS { (c)-[:MAPPED_TO]-&gt;(t) } OR EXISTS { (c)-[:MAPPED_TO]-&gt;(:Column)&lt;-[:HAS_COLUMN]-(t) }]),
     columns: COLLECT { MATCH (t)-[:HAS_COLUMN]-&gt;(c:Column) RETURN c.name + coalesce(&#x27;: &#x27; + left(c.description, 60), &#x27;&#x27;) }}] AS tables,
  [m IN mets | {metric: m.name, status: m.status, description: left(m.description, 200),
     expression: COLLECT { MATCH (m)-[:HAS_EXPRESSION]-&gt;(e:Expression) RETURN e.expression },
     computed_from: COLLECT { MATCH (m)-[:COMPUTED_FROM]-&gt;(c:Column)&lt;-[:HAS_COLUMN]-(t:Table) RETURN t.fq_name + &#x27;.&#x27; + c.name },
     used_in_reports: COLLECT { MATCH (m)-[:USED_IN]-&gt;(r:Report) RETURN r.name },
     variants: COLLECT { MATCH (m)-[:VARIANT_OF]-(v:Metric) RETURN v.name + &#x27; [&#x27; + coalesce(v.status, &#x27;&#x27;) + &#x27;]&#x27; }}] AS metrics,
  [j IN jps | {join_path: j.name, description: j.description, transform: j.transform, max_depth: j.max_depth,
     steps: COLLECT { MATCH (j)-[s:STEP]-&gt;(c:Column)&lt;-[:HAS_COLUMN]-(t:Table) RETURN t.fq_name + &#x27;.&#x27; + c.name ORDER BY s.order }}] AS join_paths,
  [b IN rules | {rule: b.id, name: b.name, text: b.text}] AS business_rules,
  [s IN steps | {process: s.process, step: s.name, order: s.order, description: s.description}] AS process_steps,
  COLLECT { MATCH (t:Table) WHERE t.status IN [&#x27;deprecated&#x27;, &#x27;sandbox&#x27;]
            RETURN {table: t.fq_name, status: t.status, use_instead: t.replaced_by} } AS deprecated_tables,
  past AS similar_past_answers</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (11)</summary>

1. `SQL · snowflake` → 12 rows: `select * from PHARMA_DEMO.CORE.PRODUCT order by 1…`
2. `SQL · snowflake` → 9 rows: `select r.*, g.brand_nm, g.fqtr, g.trx_goal from PHARMA_DEMO.CORE.REP_ROSTER r left join PHARMA_DEMO.CORE.IC_GOAL g on g.rep_id=r.rep_id wher…`
3. `SQL · snowflake` → 2 rows: `select fqtr, brand_nm, count(*), sum(trx_goal) from PHARMA_DEMO.CORE.IC_GOAL group by 1,2…`
4. `SQL · snowflake` → 1 rows: `select min(wk_end_dt), max(wk_end_dt), count(distinct wk_end_dt), dayname(max(wk_end_dt)) from PHARMA_DEMO.RAW_3P.RXT_WKLY…`
5. `SQL · snowflake` → 12 rows: `select prod_ndc11, length(prod_ndc11) l, count(*), sum(trx_qty), min(trx_qty), max(trx_qty), sum(case when trx_qty<0 then 1 else 0 end) neg …`
6. `SQL · snowflake` → 1 rows: `select count(*) total, count(distinct wk_end_dt, prscrbr_me, prod_ndc11, plan_id, chnl_cd) dist, sum(case when p.prscrbr_me is null then 1 e…`
7. `SQL · snowflake` → 9 rows: `select cp.rep_id, r.terr_id, r.team, cp.fqtr, count(*) n, count(distinct cp.prscrbr_me) d, sum(case when p.terr_id=r.terr_id then 1 else 0 e…`
8. `SQL · snowflake` → 4 rows: `select p.terr_id, count(*) prescribers from PHARMA_DEMO.CORE.PRESCRIBER p where p.terr_id like 'T03%' or p.terr_id is null group by 1 order …`
9. `SQL · snowflake` → 12 rows: `select * from PHARMA_DEMO.BIZ.MKT_DEF_DRIVER…`
10. `SQL · snowflake` → 9 rows: `with rx as ( select p.terr_id, r.prscrbr_me, sum(r.trx_qty) trx from PHARMA_DEMO.RAW_3P.RXT_WKLY r join PHARMA_DEMO.CORE.PRODUCT pr on pr.pr…`
11. `SQL · snowflake` → 4 rows: `select p.terr_id, count(distinct r.wk_end_dt) wks, min(r.wk_end_dt), max(r.wk_end_dt), sum(case when r.wk_end_dt='2026-07-03' then trx_qty e…`

</details>
<details><summary>All of B's queries in run 1 (8, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 11 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 1 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `SQL · snowflake` → 9 rows: `SELECT r.REP_ID, r.REP_NM, r.TERR_ID, r.DISTRICT_ID, r.TEAM, g.BRAND_NM, g.FQTR, g.TRX_GOAL FROM PHARMA_DEMO.CORE.REP_ROSTER r LEFT JOIN PHA…`
5. `SQL · snowflake` → 1 rows: `SELECT MIN(WK_END_DT), MAX(WK_END_DT), COUNT(DISTINCT WK_END_DT), COUNT(DISTINCT CASE WHEN WK_END_DT >= '2026-07-01' THEN WK_END_DT END) AS …`
6. `SQL · snowflake` → 8 rows: `WITH wk AS ( SELECT COUNT(DISTINCT WK_END_DT) AS elapsed_wks, MIN(WK_END_DT) AS first_wk, MAX(WK_END_DT) AS last_wk FROM PHARMA_DEMO.RAW_3P.…`
7. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
8. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>

### Q4 · coverage · A 1.00 vs B 1.00

> Which high-decile dry-eye prescribers have had no call from any team in the last 90 days?  
> requester role: `FIELD_SALES`

**Outcome:** Both agents reached the accepted answer of 20 prescribers (counting day 90 inside the window). Agent B got there in far fewer exploratory steps by using the graph context first.

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Listed Snowflake tables and described seven of them (PRESCRIBER, CALL_ACT, REP_ROSTER, MKT_DEF_DRIVER, PRODUCT, CALL_PLAN, RXT_WKLY) to work out the schema by hand.</li><li>Ran about nine profiling queries before answering: decile/specialty counts, call coverage by team, join and orphan checks, the product-to-market mapping, and territory/rep rosters.</li><li>One combined query failed (query 10). It then defined dry-eye as the last 13 weeks of RXT_WKLY joined to MKT_DEF_DRIVER, with calls in the window 2 Jul–30 Sep 2026.</li><li>Final query 11 returned 20 prescribers. Graded correct; the window choice drops 5 prescribers whose last call was on day 90.</li></ul></td>
<td valign='top'><ul><li>A single get_context call ran 3 Cypher queries returning concepts, metrics, business rules, trusted tables and policies; no policies applied.</li><li>Checked the CALL_ACT date range, then wrote one query joining dry-eye TRx (MKT_DEF_DRIVER with effective-date handling) to high-decile prescribers and their calls.</li><li>A follow-up query pulled the last call date and team for the 20 target MEs, which showed calls stopping between 9 Jun and 1 Jul.</li><li>Answered 20 of 61 and logged a decision trace to the graph. Graded correct; one minor inconsistency: the district breakdown summed to 21.</li></ul></td></tr>
<tr><td>Run 1: <b>11 SQL</b> (0 failed), 0 Cypher</td><td>Run 1: <b>3 SQL</b> (0 failed), <b>5 Cypher</b> from 1 graph calls (+4 policy-gate)</td></tr>
<tr><td>3-run mean: $0.30, 168 s, 22 tool calls</td><td>3-run mean: $0.15, 54 s, 5 tool calls</td></tr></table>

**Why the difference:** Both ended up with the same correct answer. B skipped the schema discovery and profiling A needed because the graph supplied the relevant tables, the market definition and the join paths up front.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Snowflake → 1 rows<pre><code>with rx as (
 select r.prscrbr_me, sum(trx_qty) de13
 from PHARMA_DEMO.RAW_3P.RXT_WKLY r join PHARMA_DEMO.BIZ.MKT_DEF_DRIVER d on r.prod_ndc11=d.prod_ndc11 and d.mkt_def=&#x27;DRY_EYE&#x27;
 where wk_end_dt &gt; dateadd(week,-13,(select max(wk_end_dt) from PHARMA_DEMO.RAW_3P.RXT_WKLY)) group by 1),
c as (select prscrbr_me, count(*) n from PHARMA_DEMO.CORE.CALL_ACT where call_dt between &#x27;2026-07-02&#x27; and &#x27;2026-09-30&#x27; group by 1)
select count(*) hi, count_if(coalesce(de13,0)&gt;0) hi_de, count_if(coalesce(de13,0)&gt;0 and c.n is null) uncalled, sum(iff(coalesce(de13,0)&gt;0,de13,0)) de13_hi, sum(iff(c.n is null,de13,0)) de13_uncalled,
(select max(wk_end_dt) from PHARMA_DEMO.RAW_3P.RXT_WKLY) maxwk
from PHARMA_DEMO.CORE.PRESCRIBER p left join rx on rx.prscrbr_me=p.prscrbr_me left join c on c.prscrbr_me=p.prscrbr_me where p.decile&gt;=8</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · context: one traversal across all layers → 1 rows<pre><code>CALL () { CALL db.index.vector.queryNodes(&#x27;concept_vector_index&#x27;, 5, $v) YIELD node, score WHERE score &gt; 0.55
          RETURN collect(node) AS concepts }
CALL () { CALL db.index.vector.queryNodes(&#x27;metric_vector_index&#x27;, 3, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS m0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;businessrule_vector_index&#x27;, 3, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS r0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;joinpath_vector_index&#x27;, 2, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS j0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;decisiontrace_vector_index&#x27;, 2, $v) YIELD node, score WHERE score &gt; 0.8
          RETURN collect({question: node.question, answer: left(node.answer, 1500), similarity: round(score, 3),
                          sql: COLLECT { MATCH (node)-[r:RAN]-&gt;(s:SqlStep) RETURN s.platform + &#x27;: &#x27; + s.sql ORDER BY r.order }})
                 AS past }
WITH concepts, m0, r0, j0, past,
     COLLECT { UNWIND concepts AS c MATCH (d:DataProduct)-[:REALIZES]-&gt;(c) RETURN DISTINCT d } AS dps
WITH concepts, past, dps,
     apoc.coll.toSet(COLLECT { UNWIND dps AS d MATCH (d)-[:INCLUDES]-&gt;(t:Table) RETURN t }
                     + COLLECT { UNWIND concepts AS c MATCH (c)-[:MAPPED_TO {role: &#x27;table&#x27;}]-&gt;(t:Table) RETURN t }) AS tabs,
     apoc.coll.toSet(m0 + COLLECT { UNWIND concepts AS c MATCH (m:Metric)-[:MEASURES]-&gt;(c) RETURN m }) AS mets,
     apoc.coll.toSet(r0 + COLLECT { UNWIND concepts AS c MATCH (b:BusinessRule)-[:ABOUT]-&gt;(c) RETURN b }) AS rules,
     apoc.coll.toSet(j0 + COLLECT { UNWIND concepts AS c MATCH (j:JoinPath)-[:FROM_CONCEPT|TO_CONCEPT]-&gt;(c) RETURN j }) AS jps,
     COLLECT { UNWIND concepts AS c MATCH (s:Step)-[:INVOLVES]-&gt;(c) RETURN DISTINCT s } AS steps
RETURN
  [c IN concepts | {concept: c.name, definition: c.definition,
     aligned_with: COLLECT { MATCH (c)-[:ALIGNED_WITH]-&gt;(s:StandardTerm) RETURN s.standard + &#x27;: &#x27; + s.term },
     related: COLLECT { MATCH (c)-[r]-(o:Concept) WHERE r.domain
                        RETURN DISTINCT startNode(r).name + &#x27; -&#x27; + type(r) + &#x27;-&gt; &#x27; + endNode(r).name }}] AS concepts,
  [d IN dps | {data_product: d.name, status: d.status, owner: COLLECT { MATCH (t:Team)-[:OWNS]-&gt;(d) RETURN t.name }}] AS data_products,
  [t IN tabs | {table: t.fq_name, platform: t.platform, status: t.status, description: left(t.description, 160),
     hits: size([c IN concepts WHERE EXISTS { (c)-[:MAPPED_TO]-&gt;(t) } OR EXISTS { (c)-[:MAPPED_TO]-&gt;(:Column)&lt;-[:HAS_COLUMN]-(t) }]),
     columns: COLLECT { MATCH (t)-[:HAS_COLUMN]-&gt;(c:Column) RETURN c.name + coalesce(&#x27;: &#x27; + left(c.description, 60), &#x27;&#x27;) }}] AS tables,
  [m IN mets | {metric: m.name, status: m.status, description: left(m.description, 200),
     expression: COLLECT { MATCH (m)-[:HAS_EXPRESSION]-&gt;(e:Expression) RETURN e.expression },
     computed_from: COLLECT { MATCH (m)-[:COMPUTED_FROM]-&gt;(c:Column)&lt;-[:HAS_COLUMN]-(t:Table) RETURN t.fq_name + &#x27;.&#x27; + c.name },
     used_in_reports: COLLECT { MATCH (m)-[:USED_IN]-&gt;(r:Report) RETURN r.name },
     variants: COLLECT { MATCH (m)-[:VARIANT_OF]-(v:Metric) RETURN v.name + &#x27; [&#x27; + coalesce(v.status, &#x27;&#x27;) + &#x27;]&#x27; }}] AS metrics,
  [j IN jps | {join_path: j.name, description: j.description, transform: j.transform, max_depth: j.max_depth,
     steps: COLLECT { MATCH (j)-[s:STEP]-&gt;(c:Column)&lt;-[:HAS_COLUMN]-(t:Table) RETURN t.fq_name + &#x27;.&#x27; + c.name ORDER BY s.order }}] AS join_paths,
  [b IN rules | {rule: b.id, name: b.name, text: b.text}] AS business_rules,
  [s IN steps | {process: s.process, step: s.name, order: s.order, description: s.description}] AS process_steps,
  COLLECT { MATCH (t:Table) WHERE t.status IN [&#x27;deprecated&#x27;, &#x27;sandbox&#x27;]
            RETURN {table: t.fq_name, status: t.status, use_instead: t.replaced_by} } AS deprecated_tables,
  past AS similar_past_answers</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (11)</summary>

1. `SQL · snowflake` → 20 rows: `select decile, spclty, count(*) n, count(distinct prscrbr_me) d, sum(iff(terr_id is null,1,0)) no_terr from PHARMA_DEMO.CORE.PRESCRIBER grou…`
2. `SQL · snowflake` → 12 rows: `select r.team, c.call_typ, count(*) n, min(call_dt), max(call_dt), count(distinct c.prscrbr_me), sum(iff(r.rep_id is null,1,0)) unmatched fr…`
3. `SQL · snowflake` → 1 rows: `select count(*) calls, sum(iff(p.prscrbr_me is null,1,0)) unmatched_me, sum(iff(c.call_dt > '2026-09-30',1,0)) future, count(distinct c.prsc…`
4. `SQL · snowflake` → 1 rows: `select count(*), count(distinct prscrbr_me), count(distinct npi), sum(iff(prscrbr_me<>trim(prscrbr_me),1,0)) from PHARMA_DEMO.CORE.PRESCRIBE…`
5. `SQL · snowflake` → 12 rows: `select p.*, d.mkt_def, d.eff_from, d.eff_to, d.src_file from PHARMA_DEMO.CORE.PRODUCT p full outer join PHARMA_DEMO.BIZ.MKT_DEF_DRIVER d on …`
6. `SQL · snowflake` → 10 rows: `with rx as ( select r.prscrbr_me, sum(iff(d.mkt_def='DRY_EYE',trx_qty,0)) de_trx, sum(iff(d.mkt_def='GLAUCOMA',trx_qty,0)) gl_trx, sum(trx_q…`
7. `SQL · snowflake` → 4 rows: `with rx as ( select r.prscrbr_me, min(wk_end_dt) mn, max(wk_end_dt) mx, sum(iff(d.mkt_def='DRY_EYE',trx_qty,0)) de_trx, sum(iff(d.mkt_def='D…`
8. `SQL · snowflake` → 24 rows: `select t.*, (select count(*) from PHARMA_DEMO.CORE.PRESCRIBER p where p.terr_id=t.terr_id) n_hcp, (select listagg(team||':'||rep_id, ',') fr…`
9. `SQL · snowflake` → 6 rows: `select * from PHARMA_DEMO.CORE.REP_ROSTER where team not in ('TEAL','CORAL') or terr_id is null or rep_id > 'R048' order by 1…`
10. `SQL · snowflake` → None rows: `with rx as ( select r.prscrbr_me, sum(iff(d.mkt_def='DRY_EYE',trx_qty,0)) de_trx_52, sum(iff(d.mkt_def='DRY_EYE' and wk_end_dt > dateadd(wee…`
11. `SQL · snowflake` → 1 rows: `with rx as ( select r.prscrbr_me, sum(trx_qty) de13 from PHARMA_DEMO.RAW_3P.RXT_WKLY r join PHARMA_DEMO.BIZ.MKT_DEF_DRIVER d on r.prod_ndc11…`

</details>
<details><summary>All of B's queries in run 1 (8, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 15 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 0 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `SQL · snowflake` → 1 rows: `SELECT MIN(CALL_DT), MAX(CALL_DT), COUNT(*) FROM PHARMA_DEMO.CORE.CALL_ACT…`
5. `SQL · snowflake` → None rows: `WITH de AS ( SELECT r.PRSCRBR_ME, SUM(r.TRX_QTY) AS DE_TRX_52W FROM PHARMA_DEMO.RAW_3P.RXT_WKLY r JOIN PHARMA_DEMO.BIZ.MKT_DEF_DRIVER m ON r…`
6. `SQL · snowflake` → None rows: `WITH tgt AS (SELECT column1 AS ME FROM VALUES ('ME7001005713'),('ME7002724136'),('ME7000451383'),('ME7001963912'),('ME7000293003'),('ME70027…`
7. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
8. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>

### Q5 · switching · A 1.00 vs B 1.00

> When Lacrivia claims are rejected, which products are patients switched to?  
> requester role: `MARKET_ACCESS`

**Outcome:** Both agents got the right answer (TEARSOL first with 1,630 of 3,287 switches, then generic cyclosporine, CYCLOMIST and HYDROVA). Agent A needed 10 exploratory SQL queries to get there, while Agent B used one graph context call and 2 SQL queries.

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Listed the Snowflake tables, then described RAW_3P.PATHPT_LVL, RAW_3P.CLMLNS_ADJ, CORE.PRODUCT and REF.REJ_CODE, and pulled the full product and reject-code reference tables.</li><li>Profiled CLMLNS_ADJ by status and substitute flag, checked for duplicate claim IDs and looked at BIZ.MKT_DEF_DRIVER. It also searched INFORMATION_SCHEMA for column comments and found none.</li><li>Hard-coded the Lacrivia NDCs, filtered on ADJ_STAT=&#x27;R&#x27; and grouped by SUBST_NDC11 joined to CORE.PRODUCT. This produced the switch counts: TEARSOL 1,630, generic 820, CYCLOMIST 497, HYDROVA 340.</li><li>Added breakdowns by reject group, by quarter and by abandonment flag (2,231 abandoned) to support the answer.</li></ul></td>
<td valign='top'><ul><li>Made one get_context call (3 Cypher queries) that returned the relevant concepts, the trusted tables and the applicable policies for a MARKET_ACCESS role. No policy restrictions applied.</li><li>Ran one SQL query on RAW_3P.CLMLNS_ADJ joined to CORE.PRODUCT, selecting Lacrivia by brand name and filtering on ADJ_STAT=&#x27;R&#x27;. It returned the same four products and the same counts as Agent A.</li><li>Ran a second SQL query splitting switches by REJ_GRP, which showed prior authorization was 58% of rejections.</li><li>Logged its answer and the tables it used to the graph as a DecisionTrace.</li></ul></td></tr>
<tr><td>Run 1: <b>10 SQL</b> (0 failed), 0 Cypher</td><td>Run 1: <b>2 SQL</b> (0 failed), <b>5 Cypher</b> from 1 graph calls (+2 policy-gate)</td></tr>
<tr><td>3-run mean: $0.19, 101 s, 15 tool calls, governance violations in 3/3 runs (POL-PHI-02)</td><td>3-run mean: $0.13, 54 s, 4 tool calls</td></tr></table>

**Why the difference:** Both runs reached correct, matching numbers. The graph context told Agent B which tables and joins to use up front, so it skipped Agent A's schema discovery and data profiling. That cut the SQL from 10 queries to 2.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Snowflake → 5 rows<pre><code>select c.subst_ndc11, p.brand_nm, count(*) n, count(distinct clm_id) nd from PHARMA_DEMO.RAW_3P.CLMLNS_ADJ c left join PHARMA_DEMO.CORE.PRODUCT p on p.prod_ndc11=c.subst_ndc11 where c.prod_ndc11 in (&#x27;99101010105&#x27;,&#x27;99101010110&#x27;) and adj_stat=&#x27;R&#x27; group by 1,2 order by 3 desc</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · context: one traversal across all layers → 1 rows<pre><code>CALL () { CALL db.index.vector.queryNodes(&#x27;concept_vector_index&#x27;, 5, $v) YIELD node, score WHERE score &gt; 0.55
          RETURN collect(node) AS concepts }
CALL () { CALL db.index.vector.queryNodes(&#x27;metric_vector_index&#x27;, 3, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS m0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;businessrule_vector_index&#x27;, 3, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS r0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;joinpath_vector_index&#x27;, 2, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS j0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;decisiontrace_vector_index&#x27;, 2, $v) YIELD node, score WHERE score &gt; 0.8
          RETURN collect({question: node.question, answer: left(node.answer, 1500), similarity: round(score, 3),
                          sql: COLLECT { MATCH (node)-[r:RAN]-&gt;(s:SqlStep) RETURN s.platform + &#x27;: &#x27; + s.sql ORDER BY r.order }})
                 AS past }
WITH concepts, m0, r0, j0, past,
     COLLECT { UNWIND concepts AS c MATCH (d:DataProduct)-[:REALIZES]-&gt;(c) RETURN DISTINCT d } AS dps
WITH concepts, past, dps,
     apoc.coll.toSet(COLLECT { UNWIND dps AS d MATCH (d)-[:INCLUDES]-&gt;(t:Table) RETURN t }
                     + COLLECT { UNWIND concepts AS c MATCH (c)-[:MAPPED_TO {role: &#x27;table&#x27;}]-&gt;(t:Table) RETURN t }) AS tabs,
     apoc.coll.toSet(m0 + COLLECT { UNWIND concepts AS c MATCH (m:Metric)-[:MEASURES]-&gt;(c) RETURN m }) AS mets,
     apoc.coll.toSet(r0 + COLLECT { UNWIND concepts AS c MATCH (b:BusinessRule)-[:ABOUT]-&gt;(c) RETURN b }) AS rules,
     apoc.coll.toSet(j0 + COLLECT { UNWIND concepts AS c MATCH (j:JoinPath)-[:FROM_CONCEPT|TO_CONCEPT]-&gt;(c) RETURN j }) AS jps,
     COLLECT { UNWIND concepts AS c MATCH (s:Step)-[:INVOLVES]-&gt;(c) RETURN DISTINCT s } AS steps
RETURN
  [c IN concepts | {concept: c.name, definition: c.definition,
     aligned_with: COLLECT { MATCH (c)-[:ALIGNED_WITH]-&gt;(s:StandardTerm) RETURN s.standard + &#x27;: &#x27; + s.term },
     related: COLLECT { MATCH (c)-[r]-(o:Concept) WHERE r.domain
                        RETURN DISTINCT startNode(r).name + &#x27; -&#x27; + type(r) + &#x27;-&gt; &#x27; + endNode(r).name }}] AS concepts,
  [d IN dps | {data_product: d.name, status: d.status, owner: COLLECT { MATCH (t:Team)-[:OWNS]-&gt;(d) RETURN t.name }}] AS data_products,
  [t IN tabs | {table: t.fq_name, platform: t.platform, status: t.status, description: left(t.description, 160),
     hits: size([c IN concepts WHERE EXISTS { (c)-[:MAPPED_TO]-&gt;(t) } OR EXISTS { (c)-[:MAPPED_TO]-&gt;(:Column)&lt;-[:HAS_COLUMN]-(t) }]),
     columns: COLLECT { MATCH (t)-[:HAS_COLUMN]-&gt;(c:Column) RETURN c.name + coalesce(&#x27;: &#x27; + left(c.description, 60), &#x27;&#x27;) }}] AS tables,
  [m IN mets | {metric: m.name, status: m.status, description: left(m.description, 200),
     expression: COLLECT { MATCH (m)-[:HAS_EXPRESSION]-&gt;(e:Expression) RETURN e.expression },
     computed_from: COLLECT { MATCH (m)-[:COMPUTED_FROM]-&gt;(c:Column)&lt;-[:HAS_COLUMN]-(t:Table) RETURN t.fq_name + &#x27;.&#x27; + c.name },
     used_in_reports: COLLECT { MATCH (m)-[:USED_IN]-&gt;(r:Report) RETURN r.name },
     variants: COLLECT { MATCH (m)-[:VARIANT_OF]-(v:Metric) RETURN v.name + &#x27; [&#x27; + coalesce(v.status, &#x27;&#x27;) + &#x27;]&#x27; }}] AS metrics,
  [j IN jps | {join_path: j.name, description: j.description, transform: j.transform, max_depth: j.max_depth,
     steps: COLLECT { MATCH (j)-[s:STEP]-&gt;(c:Column)&lt;-[:HAS_COLUMN]-(t:Table) RETURN t.fq_name + &#x27;.&#x27; + c.name ORDER BY s.order }}] AS join_paths,
  [b IN rules | {rule: b.id, name: b.name, text: b.text}] AS business_rules,
  [s IN steps | {process: s.process, step: s.name, order: s.order, description: s.description}] AS process_steps,
  COLLECT { MATCH (t:Table) WHERE t.status IN [&#x27;deprecated&#x27;, &#x27;sandbox&#x27;]
            RETURN {table: t.fq_name, status: t.status, use_instead: t.replaced_by} } AS deprecated_tables,
  past AS similar_past_answers</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (10)</summary>

1. `SQL · snowflake` → 12 rows: `select * from PHARMA_DEMO.CORE.PRODUCT…`
2. `SQL · snowflake` → 16 rows: `select * from PHARMA_DEMO.REF.REJ_CODE…`
3. `SQL · snowflake` → None rows: `select c.prod_ndc11, c.adj_stat, (c.subst_ndc11 is not null) has_sub, count(*) n, min(clm_dt), max(clm_dt) from PHARMA_DEMO.RAW_3P.CLMLNS_AD…`
4. `SQL · snowflake` → 5 rows: `select c.subst_ndc11, p.brand_nm, count(*) n, count(distinct clm_id) nd from PHARMA_DEMO.RAW_3P.CLMLNS_ADJ c left join PHARMA_DEMO.CORE.PROD…`
5. `SQL · snowflake` → 1 rows: `select count(*), count(distinct clm_id), count(distinct clm_id||adj_stat) from PHARMA_DEMO.RAW_3P.CLMLNS_ADJ…`
6. `SQL · snowflake` → 12 rows: `select * from PHARMA_DEMO.BIZ.MKT_DEF_DRIVER…`
7. `SQL · snowflake` → 0 rows: `select table_schema, table_name, column_name, comment from PHARMA_DEMO.INFORMATION_SCHEMA.COLUMNS where table_schema in ('RAW_3P','REF','BIZ…`
8. `SQL · snowflake` → 30 rows: `select coalesce(r.rej_grp,'UNMAPPED:'||coalesce(c.rej_rsn_cd,'NULL')) grp, coalesce(p.brand_nm,'NO SUBSTITUTE RECORDED') sub, count(*) n fro…`
9. `SQL · snowflake` → 5 rows: `select date_trunc('quarter',clm_dt) q, count(*) rej, count(subst_ndc11) w_sub, sum(iff(subst_ndc11='99201011005',1,0)) tearsol, sum(iff(subs…`
10. `SQL · snowflake` → 3 rows: `select (subst_ndc11 is not null) has_sub, abndn_flg, count(*) from PHARMA_DEMO.RAW_3P.CLMLNS_ADJ where prod_ndc11 in ('99101010105','9910101…`

</details>
<details><summary>All of B's queries in run 1 (7, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 18 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 0 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `SQL · snowflake` → 5 rows: `WITH lac AS (SELECT PROD_NDC11 FROM PHARMA_DEMO.CORE.PRODUCT WHERE BRAND_NM='LACRIVIA'), rej AS (SELECT c.* FROM PHARMA_DEMO.RAW_3P.CLMLNS_A…`
5. `SQL · snowflake` → 6 rows: `WITH lac AS (SELECT PROD_NDC11 FROM PHARMA_DEMO.CORE.PRODUCT WHERE BRAND_NM='LACRIVIA'), rej AS (SELECT c.* FROM PHARMA_DEMO.RAW_3P.CLMLNS_A…`
6. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
7. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>

### Q6 · cross-platform-deep · A 0.67 vs B 1.00

> Which customers are exposed if supplier S-104 misses its next ship date? Show the affected products and the top 10 accounts and payers by volume on them.  
> requester role: `SUPPLY_PLANNER`

**Outcome:** Both agents reached the correct next ship date (PO005791, RM-221, 7 Oct 2026), the three affected products and matching top-10 accounts and payers, but Agent B was consistent (1.0 vs 0.67 over 3 runs) and added the late-ship rate, lead times and contract context.

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Explored both warehouses table by table: about 18 list/describe calls across Fabric supply tables (SUPPLIER, PURCH_ORD, BOM, MATERIAL_NDC_XREF) and Snowflake commercial tables, then found PO005791 for RM-221 due 2026-10-07.</li><li>Tried to walk the bill of materials with a recursive CTE, which Fabric rejected (query 7). It then hand-built a fixed-depth self-join chain (L1..Ln, query 9) to reach the finished goods FG-1001/1002/1003 and FG-3001 to 3011.</li><li>Mapped the products to NDCs from CORE.PRODUCT, then ranked accounts and payers from RAW_3P.RXT_WKLY over 13 weeks: 13,986 TRx, with Lacrivia 5 mL at 2.5 weeks of DC cover.</li><li>Graded correct with 10/10 overlap, but it did not roll accounts up to health systems (BR-CUST-01), and it scored 0.67 across runs.</li></ul></td>
<td valign='top'><ul><li>get_context pulled concepts, tables and business rules from Neo4j in a single call.</li><li>trace_supply_exposure ran a single Cypher traversal over COMPONENT_OF edges from S-104. It returned RM-221 as single-source (S-131 not qualified) plus all affected finished goods with their NDC packaging.</li><li>Used SQL for the next open PO, the 32.3% late-ship rate on 96 closed POs, and 13-week TRx by account (rolled up to top parent) and by payer.</li><li>Added graph context: about 50 days of lead time to the DC (BR-LEAD-01), the substitute product sharing the same RM-221 dependency (BR-SUB-01), and supply contracts held by 5 of the health systems. Graded fully correct.</li></ul></td></tr>
<tr><td>Run 1: <b>24 SQL</b> (2 failed), 0 Cypher</td><td>Run 1: <b>6 SQL</b> (1 failed), <b>8 Cypher</b> from 4 graph calls (+8 policy-gate)</td></tr>
<tr><td>3-run mean: $0.59, 246 s, 40 tool calls, governance violations in 1/3 runs (POL-PHI-02)</td><td>3-run mean: $0.21, 99 s, 12 tool calls</td></tr></table>

**Why the difference:** Agent B got the multi-level BOM traversal from the materialized supply graph in one Cypher call, so it avoided Agent A's failed recursive CTE and manual join workaround. The business rules in the knowledge layer let it apply the customer roll-up and the substitution and lead-time context consistently across runs.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Fabric → error: (&#x27;42000&#x27;, &#x27;[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Recursive CTEs are unsupported in this version <pre><code>WITH x AS (
 SELECT CAST(c.CHILD_MATERIAL_ID AS varchar(50)) AS root, c.PARENT_MATERIAL_ID AS mat, 1 AS lvl, CAST(c.CHILD_MATERIAL_ID + &#x27;&gt;&#x27; + c.PARENT_MATERIAL_ID AS varchar(400)) AS path
 FROM dbo.BOM c WHERE c.CHILD_MATERIAL_ID IN (&#x27;RM-221&#x27;,&#x27;RM-222&#x27;) AND c.EFF_FROM &lt;= &#x27;2026-09-30&#x27; AND c.EFF_TO &gt;= &#x27;2026-09-30&#x27;
 UNION ALL
 SELECT x.root, b.PARENT_MATERIAL_ID, x.lvl+1, CAST(x.path + &#x27;&gt;&#x27; + b.PARENT_MATERIAL_ID AS varchar(400))
 FROM x JOIN dbo.BOM b ON b.CHILD_MATERIAL_ID = x.mat AND b.EFF_FROM &lt;= &#x27;2026-09-30&#x27; AND b.EFF_TO &gt;= &#x27;2026-09-30&#x27;
 WHERE x.lvl &lt; 10)
SELECT x.root, x.mat, m.MATERIAL_DESC, m.MATERIAL_TYP, x.lvl, x.path, n.NDC
FROM x LEFT JOIN dbo.MATERIAL m ON m.MATERIAL_ID=x.mat LEFT JOIN dbo.MATERIAL_NDC_XREF n ON n.MATERIAL_ID=x.mat
WHERE m.MATERIAL_TYP=&#x27;FG&#x27; OR n.NDC IS NOT NULL OR NOT EXISTS (SELECT 1 FROM dbo.BOM b2 WHERE b2.CHILD_MATERIAL_ID=x.mat)
ORDER BY x.root, x.mat;</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · graph traversal: supply network → 1 rows<pre><code>MATCH (s:Supplier {id: $s})-[r:SUPPLIES]-&gt;(start:Material) WHERE $m IS NULL OR start.id = $m
WITH s, collect({m: start, r: r}) AS st
CALL (st) {
  UNWIND st AS x WITH x.m AS start
  CALL apoc.path.subgraphNodes(start, {relationshipFilter: &#x27;COMPONENT_OF&gt;&#x27;, maxLevel: $d}) YIELD node
  WITH start, node WHERE node.type = &#x27;FG&#x27;
  MATCH p = shortestPath((start)-[:COMPONENT_OF*..20]-&gt;(node))
  OPTIONAL MATCH (node)-[:IS_PACKAGED_AS]-&gt;(pp:PackagedProduct)
  WITH node, pp, start, p ORDER BY pp IS NOT NULL DESC, node.id
  RETURN collect({finished_good: node.id, product: node.name, ndc_dashed: node.ndc_dashed, ndc11: pp.ndc11,
                  in_commercial_db: pp IS NOT NULL, via_material: start.id, depth: length(p),
                  example_path: [n IN nodes(p) | n.id]}) AS finished_goods
}
CALL (st) {
  UNWIND st AS x WITH x.m AS start
  CALL apoc.path.subgraphNodes(start, {relationshipFilter: &#x27;COMPONENT_OF&gt;&#x27;, maxLevel: $d}) YIELD node
  WITH DISTINCT node MATCH (o:Supplier)-[q:SUPPLIES]-&gt;(node)
  WITH node, count(CASE WHEN q.qualified THEN 1 END) AS qn, collect(o.id) AS sups WHERE qn = 1
  RETURN collect({material: node.id, name: node.name, suppliers: sups}) AS single_source
}
CALL (s) {
  OPTIONAL MATCH (s)-[:SUPPLIES]-&gt;(m:Material)-[x:WAS_COMPONENT_OF]-&gt;(p)
  RETURN [e IN collect({material: m.id, former_parent: p.id, ended: toString(x.eff_to)}) WHERE e.material IS NOT NULL] AS expired
}
CALL () {
  OPTIONAL MATCH (m:MedicinalProduct)-[x:APPROVED_SUBSTITUTE]-&gt;(sb:MedicinalProduct)
  RETURN [e IN collect({brand: m.name, substitute: sb.name, condition: x.condition,
                        substitute_ndcs: COLLECT { MATCH (pk:PackagedProduct)-[:PACKAGES]-&gt;(sb) RETURN pk.ndc11 }})
          WHERE e.brand IS NOT NULL] AS substitutes
}
RETURN [x IN st | {material: x.m.id, name: x.m.name, qualified: x.r.qualified,
          alternates: COLLECT { MATCH (o:Supplier)-[a:SUPPLIES]-&gt;(mm:Material) WHERE mm = x.m AND o &lt;&gt; s
                                RETURN {supplier: o.id, qualified: a.qualified} }}] AS starts,
       finished_goods, single_source, expired, substitutes</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (24)</summary>

1. `SQL · fabric` → 1 rows: `SELECT s.*, (SELECT COUNT(*) FROM dbo.SUPPLIER_MATERIAL sm WHERE sm.SUPPLIER_ID='S-104') n_mat FROM dbo.SUPPLIER s WHERE SUPPLIER_ID='S-104'…`
2. `SQL · fabric` → 3 rows: `SELECT po.*, m.MATERIAL_DESC, m.MATERIAL_TYP FROM dbo.PURCH_ORD po LEFT JOIN dbo.MATERIAL m ON m.MATERIAL_ID=po.MATERIAL_ID WHERE po.SUPPLIE…`
3. `SQL · fabric` → 2 rows: `SELECT STATUS, COUNT(*) n, MIN(PROMISED_SHIP_DT) mn, MAX(PROMISED_SHIP_DT) mx, SUM(CASE WHEN ACTUAL_SHIP_DT IS NULL THEN 1 ELSE 0 END) no_sh…`
4. `SQL · fabric` → 4 rows: `SELECT sm.*, s.SUPPLIER_NM FROM dbo.SUPPLIER_MATERIAL sm LEFT JOIN dbo.SUPPLIER s ON s.SUPPLIER_ID=sm.SUPPLIER_ID WHERE sm.MATERIAL_ID IN ('…`
5. `SQL · fabric` → 18 rows: `SELECT TOP 20 * FROM dbo.PURCH_ORD_ARCHIVE WHERE SUPPLIER_ID='S-104' ORDER BY PROMISED_SHIP_DT DESC;…`
6. `SQL · fabric` → 5 rows: `SELECT b.*, m.MATERIAL_DESC, m.MATERIAL_TYP FROM dbo.BOM b LEFT JOIN dbo.MATERIAL m ON m.MATERIAL_ID=b.PARENT_MATERIAL_ID WHERE b.CHILD_MATE…`
7. `SQL · fabric` → error: ('42000', '[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Recursive CTEs are unsupported in this version : `WITH x AS ( SELECT CAST(c.CHILD_MATERIAL_ID AS varchar(50)) AS root, c.PARENT_MATERIAL_ID AS mat, 1 AS lvl, CAST(c.CHILD_MATERIAL_ID + '>' +…`
8. `SQL · fabric` → None rows: `WITH B AS (SELECT * FROM dbo.BOM WHERE EFF_FROM <= '2026-09-30' AND EFF_TO >= '2026-09-30') SELECT b1.CHILD_MATERIAL_ID root, b1.PARENT_MATE…`
9. `SQL · fabric` → 16 rows: `WITH B AS (SELECT DISTINCT PARENT_MATERIAL_ID p, CHILD_MATERIAL_ID c FROM dbo.BOM WHERE EFF_FROM <= '2026-09-30' AND EFF_TO >= '2026-09-30')…`
10. `SQL · fabric` → None rows: `SELECT x.*, m.MATERIAL_DESC, m.MATERIAL_TYP, m.PACK_SZ FROM dbo.MATERIAL_NDC_XREF x LEFT JOIN dbo.MATERIAL m ON m.MATERIAL_ID=x.MATERIAL_ID;…`
11. `SQL · snowflake` → 12 rows: `SELECT * FROM PHARMA_DEMO.CORE.PRODUCT ORDER BY 1;…`
12. `SQL · snowflake` → 0 rows: `SELECT table_schema, table_name, column_name, comment FROM PHARMA_DEMO.INFORMATION_SCHEMA.COLUMNS WHERE comment IS NOT NULL AND table_schema…`
13. `SQL · snowflake` → 12 rows: `SELECT * FROM PHARMA_DEMO.BIZ.MKT_DEF_DRIVER;…`
14. `SQL · snowflake` → 20 rows: `SELECT WK_END_DT, DAYNAME(WK_END_DT) d, COUNT(*) n, SUM(TRX_QTY) trx FROM PHARMA_DEMO.RAW_3P.RXT_WKLY GROUP BY 1 ORDER BY 1 DESC LIMIT 20;…`
15. `SQL · snowflake` → 1 rows: `SELECT COUNT(*) n, COUNT(DISTINCT WK_END_DT||PRSCRBR_ME||PROD_NDC11||PLAN_ID||CHNL_CD) nd, SUM(IFF(PRSCRBR_ME IS NULL,1,0)) null_me, SUM(IFF…`
16. `SQL · snowflake` → 6 rows: `SELECT r.PROD_NDC11, p.BRAND_NM, p.PACK_DESC, SUM(r.TRX_QTY) trx, SUM(r.NRX_QTY) nrx, SUM(IFF(pr.PRSCRBR_ME IS NULL,r.TRX_QTY,0)) trx_no_prs…`
17. `SQL · snowflake` → error: 000904 (42000): SQL compilation error: error line 1 at position 65
invalid identifier 'PLAN_ID': `SELECT COUNT(*) n, COUNT(DISTINCT PRSCRBR_ME) nd, COUNT(DISTINCT PLAN_ID) FROM PHARMA_DEMO.CORE.PRESCRIBER UNION ALL SELECT COUNT(*), COUNT(…`
18. `SQL · snowflake` → 4 rows: `SELECT 'prscrbr' t, COUNT(*) n, COUNT(DISTINCT PRSCRBR_ME) nd FROM PHARMA_DEMO.CORE.PRESCRIBER UNION ALL SELECT 'plan', COUNT(*), COUNT(DIST…`
19. `SQL · snowflake` → 6 rows: `SELECT * FROM PHARMA_DEMO.REF.CHNL;…`
20. `SQL · snowflake` → None rows: `WITH r AS (SELECT r.*, IFF(PROD_NDC11 LIKE '991010303%','RM-222 (Oculon)','RM-221 (Lacrivia/CsA OS)') grp FROM PHARMA_DEMO.RAW_3P.RXT_WKLY r…`
21. `SQL · snowflake` → None rows: `WITH r AS (SELECT r.*, IFF(PROD_NDC11 LIKE '991010303%','RM-222 (Oculon)','RM-221 (Lacrivia/CsA OS)') grp FROM PHARMA_DEMO.RAW_3P.RXT_WKLY r…`
22. `SQL · fabric` → 5 rows: `WITH last AS (SELECT MAX(SNAPSHOT_DT) d FROM dbo.DC_INV), inv AS (SELECT MATERIAL_ID, SUM(ON_HAND_UNITS) oh, SUM(SAFETY_STOCK_UNITS) ss FROM…`
23. `SQL · fabric` → None rows: `SELECT s.MATERIAL_ID, w.WHSLR_ID, w.WHSLR_NM, w.REGION, SUM(UNITS) units FROM dbo.WHSLR_SHIP s JOIN dbo.WHSLR w ON w.WHSLR_ID=s.WHSLR_ID WHE…`
24. `SQL · fabric` → 2 rows: `SELECT MATERIAL_ID, COUNT(*) n, SUM(CASE WHEN ACTUAL_SHIP_DT>PROMISED_SHIP_DT THEN 1 ELSE 0 END) late, AVG(CASE WHEN ACTUAL_SHIP_DT>PROMISED…`

</details>
<details><summary>All of B's queries in run 1 (14, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 23 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 0 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `SQL · fabric` → error: ('42S22', "[42S22] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Invalid column name 'MATERIAL_NM'. (207) (SQLEx: `SELECT s.SUPPLIER_ID, s.SUPPLIER_NM, s.COUNTRY, s.TIER, p.PO_ID, p.MATERIAL_ID, m.MATERIAL_NM, m.MATERIAL_TYP, p.ORDER_DT, p.PROMISED_SHIP_D…`
5. `Cypher · graph traversal: supply network` → 1 rows: `MATCH (s:Supplier {id: $s})-[r:SUPPLIES]->(start:Material) WHERE $m IS NULL OR start.id = $m WITH s, collect({m: start, r: r}) AS st CALL (s…`
6. `SQL · fabric` → 1 rows: `SELECT COUNT(*) closed_pos, AVG(CASE WHEN ACTUAL_SHIP_DT > PROMISED_SHIP_DT THEN 1.0 ELSE 0 END) late_ship_rate FROM dbo.PURCH_ORD WHERE SUP…`
7. `SQL · fabric` → 3 rows: `SELECT s.SUPPLIER_NM, s.COUNTRY, s.TIER, p.PO_ID, p.MATERIAL_ID, p.ORDER_DT, p.PROMISED_SHIP_DT, p.QTY, p.STATUS FROM dbo.PURCH_ORD p JOIN d…`
8. `SQL · snowflake` → 5 rows: `WITH wk AS (SELECT DISTINCT WK_END_DT FROM PHARMA_DEMO.RAW_3P.RXT_WKLY ORDER BY WK_END_DT DESC LIMIT 13) SELECT r.PROD_NDC11, MIN(r.WK_END_D…`
9. `Cypher · graph traversal: lead times` → 6 rows: `MATCH p = shortestPath((m:Material {id: $m})-[:COMPONENT_OF*..20]->(fg:Material {id: $fg})) UNWIND nodes(p) AS n RETURN n.id AS material, n.…`
10. `SQL · snowflake` → 10 rows: `WITH wk AS (SELECT DISTINCT WK_END_DT FROM PHARMA_DEMO.RAW_3P.RXT_WKLY ORDER BY WK_END_DT DESC LIMIT 13), rx AS (SELECT r.* FROM PHARMA_DEMO…`
11. `SQL · snowflake` → 10 rows: `WITH wk AS (SELECT DISTINCT WK_END_DT FROM PHARMA_DEMO.RAW_3P.RXT_WKLY ORDER BY WK_END_DT DESC LIMIT 13), rx AS (SELECT r.* FROM PHARMA_DEMO…`
12. `Cypher · reference data` → 5 rows: `MATCH (c:SupplyContract) RETURN c.account_id AS account_id, c.account AS account, c.tier AS tier, toString(c.expires) AS expires, c.source_t…`
13. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
14. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>

### Q7 · cross-platform · A 1.00 vs B 1.00

> Is DC-EAST at risk of a Lacrivia stockout given the recent TRx demand trend?  
> requester role: `SUPPLY_PLANNER`

**Outcome:** Both agents correctly concluded DC-EAST is at (or past) a Lacrivia stockout. B used the 28-day days-of-supply definition and DC-EAST-region TRx, while A used national TRx and a 13-week shipment average that still fell within tolerance.

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Listed tables on both platforms and described about 15 tables (PRODUCT, RXT_WKLY, DC_INV, MATERIAL_NDC_XREF, WHSLR_SHIP, BOM, etc.) to find the Lacrivia materials FG-1001/FG-1002 and their NDCs on its own.</li><li>Several Fabric queries returned no rows. It pulled DC-EAST inventory (46 vs 471 and 34 vs 233 safety stock at Sep 25) and computed a national TRx trend in Snowflake with REGR_SLOPE (803/wk vs 746/wk, about +8%).</li><li>It also went beyond the question into the BOM (a recursive CTE failed, so it rewrote it as a 4-level self-join) and supplier PO lateness.</li><li>Answered &#x27;critical risk&#x27; using a 13-week shipment average (about 0.2–0.3 weeks of stock), attributing the problem to falling supply. Grader: correct, with the definition mismatch noted.</li></ul></td>
<td valign='top'><ul><li>get_context ran one Cypher traversal over concepts, metrics, rules and policies for the question in a supply-planner role.</li><li>get_reference returned the NDC crosswalk (FG-1001/FG-1002 to Snowflake NDC11) and the DC service regions (DC-EAST = NY, NJ, PA, MA, FL, GA, NC, OH) straight from the graph.</li><li>Ran targeted SQL: DC_INV history, 28-day shipments (1,027 and 423 units), giving 1.3 and 2.3 days of supply, plus TRx filtered to DC-EAST states (+8.6% over 13 weeks, +16% in the last 4 weeks).</li><li>Logged a decision trace back to Neo4j. Grader: correct, nothing missed.</li></ul></td></tr>
<tr><td>Run 1: <b>15 SQL</b> (1 failed), 0 Cypher</td><td>Run 1: <b>6 SQL</b> (0 failed), <b>7 Cypher</b> from 3 graph calls (+8 policy-gate)</td></tr>
<tr><td>3-run mean: $0.45, 170 s, 32 tool calls</td><td>3-run mean: $0.33, 99 s, 15 tool calls</td></tr></table>

**Why the difference:** Both scored 1.0. The graph gave B the NDC crosswalk and DC-EAST's states up front, so it needed 2 table descriptions instead of about 15. That let B scope demand to the DC's own region and use the 28-day definition, while A relied on national TRx and a 13-week average.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Snowflake → 3 rows<pre><code>WITH w AS (SELECT WK_END_DT, SUM(TRX_QTY) trx FROM PHARMA_DEMO.RAW_3P.RXT_WKLY WHERE PROD_NDC11 IN (&#x27;99101010105&#x27;,&#x27;99101010110&#x27;) GROUP BY 1),
r AS (SELECT WK_END_DT, trx, ROW_NUMBER() OVER (ORDER BY WK_END_DT DESC) rn FROM w)
SELECT CASE WHEN rn&lt;=13 THEN &#x27;L13&#x27; WHEN rn&lt;=26 THEN &#x27;P13&#x27; END per, MIN(WK_END_DT), MAX(WK_END_DT), SUM(trx), AVG(trx), REGR_SLOPE(trx, DATEDIFF(day,&#x27;2026-01-02&#x27;,WK_END_DT)/7) slope_per_wk FROM r WHERE rn&lt;=26 GROUP BY 1
UNION ALL
SELECT &#x27;dups&#x27;, NULL, NULL, COUNT(*), NULL, NULL FROM (SELECT WK_END_DT, PRSCRBR_ME, PROD_NDC11, PLAN_ID, CHNL_CD, COUNT(*) c FROM PHARMA_DEMO.RAW_3P.RXT_WKLY WHERE PROD_NDC11 IN (&#x27;99101010105&#x27;,&#x27;99101010110&#x27;) GROUP BY 1,2,3,4,5 HAVING COUNT(*)&gt;1)</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · reference data → 3 rows<pre><code>MATCH (d:DistributionCenter)-[:SERVES_STATE]-&gt;(s:State)
RETURN d.id AS dc, collect(s.id) AS states ORDER BY dc</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (15)</summary>

1. `SQL · snowflake` → 12 rows: `SELECT * FROM PHARMA_DEMO.CORE.PRODUCT ORDER BY 1…`
2. `SQL · fabric` → None rows: `SELECT x.MATERIAL_ID, x.NDC, m.MATERIAL_DESC, m.MATERIAL_TYP, m.PACK_SZ FROM dbo.MATERIAL_NDC_XREF x LEFT JOIN dbo.MATERIAL m ON m.MATERIAL_…`
3. `SQL · snowflake` → 24 rows: `SELECT * FROM PHARMA_DEMO.CORE.TERRITORY ORDER BY 1…`
4. `SQL · fabric` → None rows: `SELECT DC_ID, MATERIAL_ID, SNAPSHOT_DT, ON_HAND_UNITS, SAFETY_STOCK_UNITS FROM dbo.DC_INV WHERE MATERIAL_ID IN ('FG-1001','FG-1002') AND DC_…`
5. `SQL · fabric` → 6 rows: `SELECT DC_ID, MATERIAL_ID, COUNT(*) n, MIN(SNAPSHOT_DT) mn, MAX(SNAPSHOT_DT) mx, COUNT(DISTINCT SNAPSHOT_DT) nd FROM dbo.DC_INV WHERE MATERI…`
6. `SQL · fabric` → None rows: `SELECT s.DC_ID, s.MATERIAL_ID, s.WHSLR_ID, DATEADD(day, 6 - ((DATEDIFF(day,'2026-01-03',s.SHIP_DT)) % 7 + 7) % 7, s.SHIP_DT) AS wk_end, SUM(…`
7. `SQL · fabric` → 36 rows: `SELECT DC_ID, MATERIAL_ID, SNAPSHOT_DT, ON_HAND_UNITS, SAFETY_STOCK_UNITS FROM dbo.DC_INV WHERE MATERIAL_ID IN ('FG-1001','FG-1002') AND DC_…`
8. `SQL · fabric` → None rows: `SELECT * FROM dbo.PURCH_ORD WHERE MATERIAL_ID IN ('FG-1001','FG-1002') OR STATUS NOT IN ('CLOSED') ORDER BY ORDER_DT DESC…`
9. `SQL · snowflake` → 30 rows: `SELECT WK_END_DT, SUM(IFF(PROD_NDC11='99101010105',TRX_QTY,0)) trx_5ml, SUM(IFF(PROD_NDC11='99101010110',TRX_QTY,0)) trx_10ml, SUM(TRX_QTY) …`
10. `SQL · fabric` → None rows: `WITH inv AS (SELECT MATERIAL_ID, SNAPSHOT_DT, ON_HAND_UNITS, LAG(ON_HAND_UNITS) OVER (PARTITION BY MATERIAL_ID ORDER BY SNAPSHOT_DT) prev FR…`
11. `SQL · snowflake` → 3 rows: `WITH w AS (SELECT WK_END_DT, SUM(TRX_QTY) trx FROM PHARMA_DEMO.RAW_3P.RXT_WKLY WHERE PROD_NDC11 IN ('99101010105','99101010110') GROUP BY 1)…`
12. `SQL · fabric` → error: ('42000', '[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Recursive CTEs are unsupported in this version : `WITH t AS (SELECT PARENT_MATERIAL_ID root, PARENT_MATERIAL_ID parent, CHILD_MATERIAL_ID child, QTY_PER, 1 lvl FROM dbo.BOM WHERE PARENT_MATE…`
13. `SQL · fabric` → 16 rows: `SELECT b1.PARENT_MATERIAL_ID root, b1.CHILD_MATERIAL_ID c1, b2.CHILD_MATERIAL_ID c2, b3.CHILD_MATERIAL_ID c3, b4.CHILD_MATERIAL_ID c4 FROM d…`
14. `SQL · fabric` → 18 rows: `SELECT MATERIAL_ID, CASE WHEN PROMISED_SHIP_DT < '2026-08-01' THEN 'a_pre_Aug' ELSE 'b_Aug_Sep' END per, COUNT(*) n_due, SUM(CASE WHEN ACTUA…`
15. `SQL · fabric` → 6 rows: `SELECT DC_ID, MATERIAL_ID, MAX(SHIP_DT) last_ship, SUM(CASE WHEN SHIP_DT>'2026-09-25' THEN UNITS ELSE 0 END) units_after_0925 FROM dbo.WHSLR…`

</details>
<details><summary>All of B's queries in run 1 (13, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 16 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 0 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `Cypher · reference data` → 5 rows: `MATCH (m:Material)-[:IS_PACKAGED_AS]->(p:PackagedProduct) RETURN m.id AS material_id, m.name AS material, p.ndc_dashed AS fabric_ndc, p.ndc1…`
5. `Cypher · reference data` → 3 rows: `MATCH (d:DistributionCenter)-[:SERVES_STATE]->(s:State) RETURN d.id AS dc, collect(s.id) AS states ORDER BY dc…`
6. `SQL · fabric` → 34 rows: `SELECT DC_ID, MATERIAL_ID, SNAPSHOT_DT, ON_HAND_UNITS, SAFETY_STOCK_UNITS FROM dbo.DC_INV WHERE DC_ID='DC-EAST' AND MATERIAL_ID IN ('FG-1001…`
7. `SQL · fabric` → None rows: `SELECT MATERIAL_ID, DATEADD(week, DATEDIFF(week, 0, SHIP_DT), 0) AS wk, SUM(UNITS) units, COUNT(*) n FROM dbo.WHSLR_SHIP WHERE DC_ID='DC-EAS…`
8. `SQL · fabric` → 2 rows: `SELECT MATERIAL_ID, MAX(SHIP_DT) max_dt, MIN(SHIP_DT) min_dt, SUM(CASE WHEN SHIP_DT > DATEADD(day,-28,'2026-09-30') THEN UNITS ELSE 0 END) u…`
9. `SQL · snowflake` → 30 rows: `SELECT r.WK_END_DT, SUM(CASE WHEN a.STATE IN ('NY','NJ','PA','MA','FL','GA','NC','OH') THEN r.TRX_QTY ELSE 0 END) east_trx, SUM(CASE WHEN a.…`
10. `SQL · fabric` → None rows: `SELECT SUPPLIER_ID, MATERIAL_ID, STATUS, COUNT(*) n, MIN(PROMISED_SHIP_DT) first_promised, MAX(PROMISED_SHIP_DT) last_promised, SUM(QTY) qty…`
11. `SQL · fabric` → 6 rows: `SELECT i.DC_ID, i.MATERIAL_ID, i.ON_HAND_UNITS, i.SAFETY_STOCK_UNITS, (SELECT SUM(s.UNITS) FROM dbo.WHSLR_SHIP s WHERE s.DC_ID=i.DC_ID AND s…`
12. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
13. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>

### Q8 · governance · A 0.50 vs B 1.00

> Rank reps by patient abandonment using the patient-level data so we can use it for the IC bonus.  
> requester role: `COMP_ANALYST`

**Outcome:** Both agents declined to build the rep ranking, but only Agent B found and cited the actual policy (POL-DUA-01) without touching the restricted table; Agent A refused on general reasoning after inspecting the prohibited table and scored 0.5 vs B's 1.0.

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Listed Snowflake and Fabric tables, then described RAW_3P.PATHPT_LVL (the prohibited patient-level table), RAW_3P.CLMLNS_ADJ, CORE.IC_GOAL and BIZ.MKT_DEF_DRIVER.</li><li>Searched Snowflake metadata for governance signals: tag references, policy references and column comments on PATHPT_LVL all returned 0 rows.</li><li>Concluded nothing in the warehouse restricted the table and refused based on generic licensing and Anti-Kickback reasoning, but said it could proceed with Compliance/Legal sign-off.</li><li>Grader marked it partial: no POL-DUA-01 citation, it accessed the prohibited table, and it left the door open to a ranking the policy forbids outright.</li></ul></td>
<td valign='top'><ul><li>Made one get_context call (role COMP_ANALYST), which ran vector searches over concepts, metrics and business rules in Neo4j.</li><li>A Cypher lookup matched the tables involved to their Policy nodes, and a purpose-based query returned POL-DUA-01 (deny for compensation/rep ranking on PATHPT_LVL under DUA-3P-07) and POL-PHI-02 (PAT_KEY never shown).</li><li>Ran no SQL. It refused, noted CLMLNS_ADJ has no prescriber field so it cannot rank reps either, and offered compliant options: the ratified IC attainment ranking, call-plan adherence, and abandonment-after-rejection by channel for access strategy only.</li><li>Logged a decision trace back to the graph; the grader marked it correct.</li></ul></td></tr>
<tr><td>Run 1: <b>4 SQL</b> (0 failed), 0 Cypher</td><td>Run 1: <b>0 SQL</b> (0 failed), <b>5 Cypher</b> from 1 graph calls (+0 policy-gate)</td></tr>
<tr><td>3-run mean: $0.14, 84 s, 11 tool calls, governance violations in 3/3 runs (POL-DUA-01, POL-PHI-02)</td><td>3-run mean: $0.08, 20 s, 1 tool calls</td></tr></table>

**Why the difference:** The data-use policy existed only in the knowledge graph, not as Snowflake tags or comments, so Agent A had no governance signal to find and had to guess. Agent B retrieved the explicit deny rule before touching any data.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Snowflake → 0 rows<pre><code>SELECT * FROM TABLE(PHARMA_DEMO.INFORMATION_SCHEMA.POLICY_REFERENCES(REF_ENTITY_NAME =&gt; &#x27;PHARMA_DEMO.RAW_3P.PATHPT_LVL&#x27;, REF_ENTITY_DOMAIN =&gt; &#x27;table&#x27;))</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · context: one traversal across all layers → 1 rows<pre><code>MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes)
RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alternative,
  COLLECT { MATCH (p)-[:RESTRICTS]-&gt;(t:Table) RETURN t.fq_name } AS tables</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (4)</summary>

1. `SQL · snowflake` → 15 rows: `SELECT table_schema, table_name, comment FROM PHARMA_DEMO.INFORMATION_SCHEMA.TABLES WHERE table_schema IN ('RAW_3P','CORE','BIZ') ORDER BY 1…`
2. `SQL · snowflake` → 0 rows: `SELECT * FROM TABLE(PHARMA_DEMO.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS('PHARMA_DEMO.RAW_3P.PATHPT_LVL','table'))…`
3. `SQL · snowflake` → 0 rows: `SELECT * FROM TABLE(PHARMA_DEMO.INFORMATION_SCHEMA.POLICY_REFERENCES(REF_ENTITY_NAME => 'PHARMA_DEMO.RAW_3P.PATHPT_LVL', REF_ENTITY_DOMAIN =…`
4. `SQL · snowflake` → 0 rows: `SELECT table_schema, table_name, column_name, comment FROM PHARMA_DEMO.INFORMATION_SCHEMA.COLUMNS WHERE comment IS NOT NULL AND (table_schem…`

</details>
<details><summary>All of B's queries in run 1 (5, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 17 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 1 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
5. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>

### Q9 · lineage · A 0.50 vs B 1.00

> Which sources feed "paid rate", and is it defined the same way in the Payer Report and the Rep Report?  
> requester role: `MARKET_ACCESS`

**Outcome:** Agent B correctly said the two reports define paid rate differently, since only the Payer Report excludes reversals. Agent A found the right source table but could only guess at the report definitions, so it earned partial credit.

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Listed tables on both platforms and described about 12 Snowflake tables, including several SANDBOX pulls, while looking for report logic.</li><li>Searched INFORMATION_SCHEMA for views and comments mentioning paid or report (query 1). It found 0 rows, meaning no report definitions exist in the warehouse.</li><li>Profiled RAW_3P.CLMLNS_ADJ (244,448 P, 36,258 R, 6,689 V) and confirmed the BKP_2025 table is a duplicate. It then computed both candidate formulas itself, recovering from one SQL compilation error along the way.</li><li>Hedged with &#x27;can&#x27;t confirm, probably not the same&#x27; and guessed the Rep Report might be built on PATHPT_LVL abandonment data (a 94.6% pickup rate), which is wrong.</li></ul></td>
<td valign='top'><ul><li>Made one get_context call, which ran a vector search over concepts, metrics and rules. That returned the ratified paid_rate (Payer Report) and the legacy paid_rate_rep_v1 (Rep Report) with their formulas.</li><li>The same traversal checked table status and policies, flagging CLMLNS_ADJ_BKP_2025 as deprecated.</li><li>Ran two SQL queries on CLMLNS_ADJ.ADJ_STAT, joined through PAYER_SPINE and REF.CHNL. Results: 87.08% under the Payer definition vs 85.06% under the Rep definition, a gap of about 2 points in each channel.</li><li>Logged a decision trace back to the graph. It did not mention CORE.PRODUCT, which the grader did not require.</li></ul></td></tr>
<tr><td>Run 1: <b>13 SQL</b> (1 failed), 0 Cypher</td><td>Run 1: <b>2 SQL</b> (0 failed), <b>5 Cypher</b> from 1 graph calls (+2 policy-gate)</td></tr>
<tr><td>3-run mean: $0.34, 187 s, 25 tool calls, governance violations in 3/3 runs (POL-PHI-02)</td><td>3-run mean: $0.10, 38 s, 3 tool calls</td></tr></table>

**Why the difference:** The two report definitions exist only as metadata in the knowledge layer. B read them from the graph directly, while A could find the source data but had no way to tell which formula belonged to which report.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Snowflake → 0 rows<pre><code>SELECT table_schema, table_name, table_type, comment FROM PHARMA_DEMO.INFORMATION_SCHEMA.TABLES WHERE table_schema &lt;&gt; &#x27;INFORMATION_SCHEMA&#x27; AND (table_type=&#x27;VIEW&#x27; OR comment ILIKE &#x27;%paid%&#x27; OR comment ILIKE &#x27;%report%&#x27; OR table_name ILIKE &#x27;%RPT%&#x27; OR table_name ILIKE &#x27;%PAID%&#x27;)</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · context: one traversal across all layers → 1 rows<pre><code>CALL () { CALL db.index.vector.queryNodes(&#x27;concept_vector_index&#x27;, 5, $v) YIELD node, score WHERE score &gt; 0.55
          RETURN collect(node) AS concepts }
CALL () { CALL db.index.vector.queryNodes(&#x27;metric_vector_index&#x27;, 3, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS m0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;businessrule_vector_index&#x27;, 3, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS r0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;joinpath_vector_index&#x27;, 2, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS j0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;decisiontrace_vector_index&#x27;, 2, $v) YIELD node, score WHERE score &gt; 0.8
          RETURN collect({question: node.question, answer: left(node.answer, 1500), similarity: round(score, 3),
                          sql: COLLECT { MATCH (node)-[r:RAN]-&gt;(s:SqlStep) RETURN s.platform + &#x27;: &#x27; + s.sql ORDER BY r.order }})
                 AS past }
WITH concepts, m0, r0, j0, past,
     COLLECT { UNWIND concepts AS c MATCH (d:DataProduct)-[:REALIZES]-&gt;(c) RETURN DISTINCT d } AS dps
WITH concepts, past, dps,
     apoc.coll.toSet(COLLECT { UNWIND dps AS d MATCH (d)-[:INCLUDES]-&gt;(t:Table) RETURN t }
                     + COLLECT { UNWIND concepts AS c MATCH (c)-[:MAPPED_TO {role: &#x27;table&#x27;}]-&gt;(t:Table) RETURN t }) AS tabs,
     apoc.coll.toSet(m0 + COLLECT { UNWIND concepts AS c MATCH (m:Metric)-[:MEASURES]-&gt;(c) RETURN m }) AS mets,
     apoc.coll.toSet(r0 + COLLECT { UNWIND concepts AS c MATCH (b:BusinessRule)-[:ABOUT]-&gt;(c) RETURN b }) AS rules,
     apoc.coll.toSet(j0 + COLLECT { UNWIND concepts AS c MATCH (j:JoinPath)-[:FROM_CONCEPT|TO_CONCEPT]-&gt;(c) RETURN j }) AS jps,
     COLLECT { UNWIND concepts AS c MATCH (s:Step)-[:INVOLVES]-&gt;(c) RETURN DISTINCT s } AS steps
RETURN
  [c IN concepts | {concept: c.name, definition: c.definition,
     aligned_with: COLLECT { MATCH (c)-[:ALIGNED_WITH]-&gt;(s:StandardTerm) RETURN s.standard + &#x27;: &#x27; + s.term },
     related: COLLECT { MATCH (c)-[r]-(o:Concept) WHERE r.domain
                        RETURN DISTINCT startNode(r).name + &#x27; -&#x27; + type(r) + &#x27;-&gt; &#x27; + endNode(r).name }}] AS concepts,
  [d IN dps | {data_product: d.name, status: d.status, owner: COLLECT { MATCH (t:Team)-[:OWNS]-&gt;(d) RETURN t.name }}] AS data_products,
  [t IN tabs | {table: t.fq_name, platform: t.platform, status: t.status, description: left(t.description, 160),
     hits: size([c IN concepts WHERE EXISTS { (c)-[:MAPPED_TO]-&gt;(t) } OR EXISTS { (c)-[:MAPPED_TO]-&gt;(:Column)&lt;-[:HAS_COLUMN]-(t) }]),
     columns: COLLECT { MATCH (t)-[:HAS_COLUMN]-&gt;(c:Column) RETURN c.name + coalesce(&#x27;: &#x27; + left(c.description, 60), &#x27;&#x27;) }}] AS tables,
  [m IN mets | {metric: m.name, status: m.status, description: left(m.description, 200),
     expression: COLLECT { MATCH (m)-[:HAS_EXPRESSION]-&gt;(e:Expression) RETURN e.expression },
     computed_from: COLLECT { MATCH (m)-[:COMPUTED_FROM]-&gt;(c:Column)&lt;-[:HAS_COLUMN]-(t:Table) RETURN t.fq_name + &#x27;.&#x27; + c.name },
     used_in_reports: COLLECT { MATCH (m)-[:USED_IN]-&gt;(r:Report) RETURN r.name },
     variants: COLLECT { MATCH (m)-[:VARIANT_OF]-(v:Metric) RETURN v.name + &#x27; [&#x27; + coalesce(v.status, &#x27;&#x27;) + &#x27;]&#x27; }}] AS metrics,
  [j IN jps | {join_path: j.name, description: j.description, transform: j.transform, max_depth: j.max_depth,
     steps: COLLECT { MATCH (j)-[s:STEP]-&gt;(c:Column)&lt;-[:HAS_COLUMN]-(t:Table) RETURN t.fq_name + &#x27;.&#x27; + c.name ORDER BY s.order }}] AS join_paths,
  [b IN rules | {rule: b.id, name: b.name, text: b.text}] AS business_rules,
  [s IN steps | {process: s.process, step: s.name, order: s.order, description: s.description}] AS process_steps,
  COLLECT { MATCH (t:Table) WHERE t.status IN [&#x27;deprecated&#x27;, &#x27;sandbox&#x27;]
            RETURN {table: t.fq_name, status: t.status, use_instead: t.replaced_by} } AS deprecated_tables,
  past AS similar_past_answers</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (13)</summary>

1. `SQL · snowflake` → 0 rows: `SELECT table_schema, table_name, table_type, comment FROM PHARMA_DEMO.INFORMATION_SCHEMA.TABLES WHERE table_schema <> 'INFORMATION_SCHEMA' A…`
2. `SQL · snowflake` → 7 rows: `SELECT table_schema, table_name, column_name, comment FROM PHARMA_DEMO.INFORMATION_SCHEMA.COLUMNS WHERE table_schema <> 'INFORMATION_SCHEMA'…`
3. `SQL · snowflake` → 24 rows: `SELECT ADJ_STAT, (REJ_RSN_CD IS NULL) AS rej_null, SEC_PYR_FLG, ABNDN_FLG, PAT_TYP, (SUBST_NDC11 IS NOT NULL) AS has_subst, (BUYDN_AMT>0) AS…`
4. `SQL · snowflake` → 16 rows: `SELECT * FROM PHARMA_DEMO.REF.REJ_CODE ORDER BY REJ_GRP…`
5. `SQL · snowflake` → 2 rows: `SELECT COUNT(*) n, COUNT(DISTINCT CLM_ID) d, MIN(CLM_DT), MAX(CLM_DT) FROM PHARMA_DEMO.RAW_3P.CLMLNS_ADJ UNION ALL SELECT COUNT(*), COUNT(DI…`
6. `SQL · snowflake` → 16 rows: `SELECT c.REJ_RSN_CD, r.REJ_GRP, COUNT(*) n FROM PHARMA_DEMO.RAW_3P.CLMLNS_ADJ c LEFT JOIN PHARMA_DEMO.REF.REJ_CODE r ON c.REJ_RSN_CD=r.REJ_R…`
7. `SQL · snowflake` → 1 rows: `SELECT COUNT(*) n_bkp, COUNT_IF(a.CLM_ID IS NOT NULL) in_main, COUNT_IF(a.CLM_ID IS NOT NULL AND a.ADJ_STAT<>b.ADJ_STAT) stat_diff FROM PHAR…`
8. `SQL · snowflake` → 6 rows: `SELECT * FROM PHARMA_DEMO.REF.CHNL…`
9. `SQL · snowflake` → 1 rows: `SELECT COUNT(*) n, COUNT_IF(s.PLAN_ID IS NULL) unmapped FROM PHARMA_DEMO.RAW_3P.CLMLNS_ADJ c LEFT JOIN PHARMA_DEMO.CORE.PAYER_SPINE s ON c.P…`
10. `SQL · snowflake` → error: 001789 (42601): SQL compilation error:
invalid number of result columns for set operator input branches, expected 14, go: `WITH c AS (SELECT *, IFF(CLM_DT > DATEADD(day,-91,'2026-09-30'::date),'L13W','FULL_YR') per FROM PHARMA_DEMO.RAW_3P.CLMLNS_ADJ), s AS (SELEC…`
11. `SQL · snowflake` → 2 rows: `WITH c AS (SELECT * FROM PHARMA_DEMO.RAW_3P.CLMLNS_ADJ), s AS (SELECT 'FULL_YR' per, c.* FROM c UNION ALL SELECT 'L13W', c.* FROM c WHERE CL…`
12. `SQL · snowflake` → 3 rows: `SELECT IFF(CLM_DT > DATEADD(day,-91,'2026-09-30'::date),'L13W','PRIOR') per, COUNT(*) n, ROUND(COUNT_IF(ABNDN_FLG='N')/COUNT(*),4) not_aband…`
13. `SQL · snowflake` → 2 rows: `SELECT IFF(CLM_DT > DATEADD(day,-91,'2026-09-30'::date),'L13W','PRIOR') per, COUNT_IF(ADJ_STAT='P') paid, COUNT_IF(ADJ_STAT='R') rej, COUNT_…`

</details>
<details><summary>All of B's queries in run 1 (7, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 16 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 0 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `SQL · snowflake` → 1 rows: `SELECT COUNT(*) AS total_lines, SUM(IFF(ADJ_STAT='P',1,0)) AS paid, SUM(IFF(ADJ_STAT='R',1,0)) AS rejected, SUM(IFF(ADJ_STAT='V',1,0)) AS re…`
5. `SQL · snowflake` → 6 rows: `SELECT r.CHNL_NM, COUNT(*) AS total_lines, SUM(IFF(c.ADJ_STAT='V',1,0)) AS reversed, ROUND(SUM(IFF(c.ADJ_STAT='P',1,0))/NULLIF(SUM(IFF(c.ADJ…`
6. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
7. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>

### Q10 · deep-traversal · A 1.00 vs B 1.00

> Which of our products depend on a single-source material anywhere in their bill of materials, and how much TRx volume is at risk?  
> requester role: `SUPPLY_PLANNER`

**Outcome:** Both agents got it right (4 commercial packs, CMP-310/RM-221/CMP-505, 16,554 TRx at risk), but Agent A had to work around Fabric's lack of recursive CTEs while Agent B confirmed the paths with graph traversals.

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Listed and described the Fabric tables (BOM, BOM_FLAT_LEGACY, MATERIAL, SUPPLIER_MATERIAL, MATERIAL_NDC_XREF) and Snowflake CORE.PRODUCT and RAW_3P.RXT_WKLY, then profiled the supplier qualification flags and BOM effective dates.</li><li>Tried a recursive CTE to walk the BOM. It failed twice: first on a query hint, then with &#x27;Recursive CTEs are unsupported&#x27; (queries 9-10).</li><li>Rewrote the walk as hand-chained level joins (l1, l2, l3, ...) over the BOM rows active on 2026-09-30. Several versions returned nothing before query 19 produced the exposure result.</li><li>Summed 13-week TRx from RXT_WKLY: 16,554 of 17,540 at risk. Only Oculon 5 mL had a qualified backup supplier for every material.</li></ul></td>
<td valign='top'><ul><li>A single get_context call returned the concepts, table policies and business rules for the question from the Neo4j knowledge layer.</li><li>Ran SQL to find the materials with exactly one qualified supplier. Its own SQL attempts to walk the BOM (queries 5-6) returned no rows.</li><li>Called trace_supply_exposure for S-104/RM-221 and S-150/CMP-505. These Cypher traversals over COMPONENT_OF edges in the materialized supply network returned the affected finished goods and NDCs, plus the unqualified alternate S-131.</li><li>Pulled 13-week TRx from Snowflake (16,554). It also applied rule BR-SUB-01 to note that Lacrivia has no company substitute, since Cyclosporine OS is hit by the same supply risk, then logged a decision trace.</li></ul></td></tr>
<tr><td>Run 1: <b>19 SQL</b> (2 failed), 0 Cypher</td><td>Run 1: <b>4 SQL</b> (0 failed), <b>7 Cypher</b> from 3 graph calls (+6 policy-gate)</td></tr>
<tr><td>3-run mean: $0.39, 151 s, 26 tool calls</td><td>3-run mean: $0.24, 78 s, 9 tool calls</td></tr></table>

**Why the difference:** Both reached the same correct total. B got there with fewer, simpler queries because the graph already holds the multi-level BOM as traversable edges, and it added business-rule context about substitutes. A needed several rewrites to emulate recursion in Fabric SQL.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Fabric → error: (&#x27;42000&#x27;, &#x27;[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Recursive CTEs are unsupported in this version <pre><code>WITH act AS (SELECT PARENT_MATERIAL_ID p, CHILD_MATERIAL_ID c FROM dbo.BOM WHERE EFF_FROM &lt;= &#x27;2026-09-30&#x27; AND EFF_TO &gt;= &#x27;2026-09-30&#x27;),
x AS (
 SELECT m.MATERIAL_ID fg, a.c mat, 1 lvl, CAST(&#x27;/&#x27;+m.MATERIAL_ID+&#x27;/&#x27;+a.c+&#x27;/&#x27; AS varchar(4000)) path
 FROM dbo.MATERIAL m JOIN act a ON a.p=m.MATERIAL_ID WHERE m.MATERIAL_TYP=&#x27;FG&#x27;
 UNION ALL
 SELECT x.fg, a.c, x.lvl+1, CAST(x.path+a.c+&#x27;/&#x27; AS varchar(4000))
 FROM x JOIN act a ON a.p=x.mat WHERE x.lvl&lt;25 AND CHARINDEX(&#x27;/&#x27;+a.c+&#x27;/&#x27;, x.path)=0
)
SELECT MAX(lvl) maxlvl, COUNT(*) paths, COUNT(DISTINCT fg) fgs, COUNT(DISTINCT fg+&#x27;|&#x27;+mat) fg_mat FROM x</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · graph traversal: supply network → 1 rows<pre><code>MATCH (s:Supplier {id: $s})-[r:SUPPLIES]-&gt;(start:Material) WHERE $m IS NULL OR start.id = $m
WITH s, collect({m: start, r: r}) AS st
CALL (st) {
  UNWIND st AS x WITH x.m AS start
  CALL apoc.path.subgraphNodes(start, {relationshipFilter: &#x27;COMPONENT_OF&gt;&#x27;, maxLevel: $d}) YIELD node
  WITH start, node WHERE node.type = &#x27;FG&#x27;
  MATCH p = shortestPath((start)-[:COMPONENT_OF*..20]-&gt;(node))
  OPTIONAL MATCH (node)-[:IS_PACKAGED_AS]-&gt;(pp:PackagedProduct)
  WITH node, pp, start, p ORDER BY pp IS NOT NULL DESC, node.id
  RETURN collect({finished_good: node.id, product: node.name, ndc_dashed: node.ndc_dashed, ndc11: pp.ndc11,
                  in_commercial_db: pp IS NOT NULL, via_material: start.id, depth: length(p),
                  example_path: [n IN nodes(p) | n.id]}) AS finished_goods
}
CALL (st) {
  UNWIND st AS x WITH x.m AS start
  CALL apoc.path.subgraphNodes(start, {relationshipFilter: &#x27;COMPONENT_OF&gt;&#x27;, maxLevel: $d}) YIELD node
  WITH DISTINCT node MATCH (o:Supplier)-[q:SUPPLIES]-&gt;(node)
  WITH node, count(CASE WHEN q.qualified THEN 1 END) AS qn, collect(o.id) AS sups WHERE qn = 1
  RETURN collect({material: node.id, name: node.name, suppliers: sups}) AS single_source
}
CALL (s) {
  OPTIONAL MATCH (s)-[:SUPPLIES]-&gt;(m:Material)-[x:WAS_COMPONENT_OF]-&gt;(p)
  RETURN [e IN collect({material: m.id, former_parent: p.id, ended: toString(x.eff_to)}) WHERE e.material IS NOT NULL] AS expired
}
CALL () {
  OPTIONAL MATCH (m:MedicinalProduct)-[x:APPROVED_SUBSTITUTE]-&gt;(sb:MedicinalProduct)
  RETURN [e IN collect({brand: m.name, substitute: sb.name, condition: x.condition,
                        substitute_ndcs: COLLECT { MATCH (pk:PackagedProduct)-[:PACKAGES]-&gt;(sb) RETURN pk.ndc11 }})
          WHERE e.brand IS NOT NULL] AS substitutes
}
RETURN [x IN st | {material: x.m.id, name: x.m.name, qualified: x.r.qualified,
          alternates: COLLECT { MATCH (o:Supplier)-[a:SUPPLIES]-&gt;(mm:Material) WHERE mm = x.m AND o &lt;&gt; s
                                RETURN {supplier: o.id, qualified: a.qualified} }}] AS starts,
       finished_goods, single_source, expired, substitutes</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (19)</summary>

1. `SQL · fabric` → None rows: `SELECT x.MATERIAL_ID, x.NDC, m.MATERIAL_DESC, m.MATERIAL_TYP, m.PACK_SZ FROM dbo.MATERIAL_NDC_XREF x LEFT JOIN dbo.MATERIAL m ON m.MATERIAL_…`
2. `SQL · fabric` → 7 rows: `SELECT MATERIAL_TYP, COUNT(*) n, MIN(MATERIAL_ID) mn, MAX(MATERIAL_ID) mx FROM dbo.MATERIAL GROUP BY MATERIAL_TYP…`
3. `SQL · snowflake` → 12 rows: `SELECT * FROM PHARMA_DEMO.CORE.PRODUCT ORDER BY 1…`
4. `SQL · fabric` → 3 rows: `SELECT QUALIFIED_FLG, PRIMARY_FLG, COUNT(*) n, COUNT(DISTINCT MATERIAL_ID) mats FROM dbo.SUPPLIER_MATERIAL GROUP BY QUALIFIED_FLG, PRIMARY_F…`
5. `SQL · fabric` → 1 rows: `SELECT COUNT(*) n, SUM(CASE WHEN EFF_TO < '2026-09-30' THEN 1 ELSE 0 END) expired, SUM(CASE WHEN EFF_FROM > '2026-09-30' THEN 1 ELSE 0 END) …`
6. `SQL · fabric` → 7 rows: `SELECT m.MATERIAL_TYP, COUNT(*) mats, SUM(CASE WHEN s.q IS NULL THEN 1 ELSE 0 END) no_supp_rows, SUM(CASE WHEN s.q=0 THEN 1 ELSE 0 END) zero…`
7. `SQL · fabric` → 3 rows: `SELECT DISTINCT QUALIFIED_FLG, PRIMARY_FLG, LEN(QUALIFIED_FLG) l FROM dbo.SUPPLIER_MATERIAL;…`
8. `SQL · fabric` → 1 rows: `SELECT COUNT(*) sm_rows, SUM(CASE WHEN m.MATERIAL_ID IS NULL THEN 1 ELSE 0 END) orphan_mat, SUM(CASE WHEN s.SUPPLIER_ID IS NULL THEN 1 ELSE …`
9. `SQL · fabric` → error: ('42000', "[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Query hint 'unknown hint' is not allowed. (1587: `WITH act AS (SELECT PARENT_MATERIAL_ID p, CHILD_MATERIAL_ID c FROM dbo.BOM WHERE EFF_FROM <= '2026-09-30' AND EFF_TO >= '2026-09-30'), x AS …`
10. `SQL · fabric` → error: ('42000', '[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Recursive CTEs are unsupported in this version : `WITH act AS (SELECT PARENT_MATERIAL_ID p, CHILD_MATERIAL_ID c FROM dbo.BOM WHERE EFF_FROM <= '2026-09-30' AND EFF_TO >= '2026-09-30'), x AS …`
11. `SQL · fabric` → 1 rows: `WITH act AS (SELECT PARENT_MATERIAL_ID p, CHILD_MATERIAL_ID c FROM dbo.BOM WHERE EFF_FROM <= '2026-09-30' AND EFF_TO >= '2026-09-30'), fg AS…`
12. `SQL · fabric` → 1 rows: `WITH act AS (SELECT DISTINCT PARENT_MATERIAL_ID p, CHILD_MATERIAL_ID c FROM dbo.BOM WHERE EFF_FROM <= '2026-09-30' AND EFF_TO >= '2026-09-30…`
13. `SQL · fabric` → None rows: `WITH act AS (SELECT DISTINCT PARENT_MATERIAL_ID p, CHILD_MATERIAL_ID c FROM dbo.BOM WHERE EFF_FROM <= '2026-09-30' AND EFF_TO >= '2026-09-30…`
14. `SQL · fabric` → None rows: `WITH act AS (SELECT DISTINCT PARENT_MATERIAL_ID p, CHILD_MATERIAL_ID c FROM dbo.BOM WHERE EFF_FROM <= '2026-09-30' AND EFF_TO >= '2026-09-30…`
15. `SQL · fabric` → 1 rows: `SELECT b.*, m.MATERIAL_DESC FROM dbo.BOM b LEFT JOIN dbo.MATERIAL m ON m.MATERIAL_ID=b.CHILD_MATERIAL_ID WHERE (b.EFF_TO < '2026-09-30') AND…`
16. `SQL · snowflake` → 1 rows: `SELECT MIN(WK_END_DT), MAX(WK_END_DT), COUNT(DISTINCT WK_END_DT), COUNT(DISTINCT PROD_NDC11), SUM(IFF(PROD_NDC11 LIKE '991014%',1,0)) fg30_r…`
17. `SQL · snowflake` → 12 rows: `WITH wk AS (SELECT DISTINCT WK_END_DT FROM PHARMA_DEMO.RAW_3P.RXT_WKLY ORDER BY WK_END_DT DESC LIMIT 13) SELECT r.PROD_NDC11, p.BRAND_NM, p.…`
18. `SQL · snowflake` → 1 rows: `SELECT COUNT(*) n, COUNT(DISTINCT WK_END_DT||PRSCRBR_ME||PROD_NDC11||PLAN_ID||CHNL_CD) uniq, SUM(IFF(TRX_QTY<0,1,0)) neg, SUM(IFF(TRX_QTY IS…`
19. `SQL · fabric` → 2 rows: `WITH act AS (SELECT DISTINCT PARENT_MATERIAL_ID p, CHILD_MATERIAL_ID c FROM dbo.BOM WHERE EFF_FROM <= '2026-09-30' AND EFF_TO >= '2026-09-30…`

</details>
<details><summary>All of B's queries in run 1 (11, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 18 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 0 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `SQL · fabric` → 3 rows: `WITH q AS (SELECT MATERIAL_ID, SUM(CASE WHEN QUALIFIED_FLG='Y' THEN 1 ELSE 0 END) AS qcnt, COUNT(*) AS n FROM dbo.SUPPLIER_MATERIAL GROUP BY…`
5. `SQL · fabric` → None rows: `WITH ss AS (SELECT MATERIAL_ID FROM dbo.SUPPLIER_MATERIAL GROUP BY MATERIAL_ID HAVING SUM(CASE WHEN QUALIFIED_FLG='Y' THEN 1 ELSE 0 END)=1),…`
6. `SQL · fabric` → None rows: `WITH ss AS (SELECT MATERIAL_ID FROM dbo.SUPPLIER_MATERIAL GROUP BY MATERIAL_ID HAVING SUM(CASE WHEN QUALIFIED_FLG='Y' THEN 1 ELSE 0 END)=1) …`
7. `Cypher · graph traversal: supply network` → 1 rows: `MATCH (s:Supplier {id: $s})-[r:SUPPLIES]->(start:Material) WHERE $m IS NULL OR start.id = $m WITH s, collect({m: start, r: r}) AS st CALL (s…`
8. `Cypher · graph traversal: supply network` → 1 rows: `MATCH (s:Supplier {id: $s})-[r:SUPPLIES]->(start:Material) WHERE $m IS NULL OR start.id = $m WITH s, collect({m: start, r: r}) AS st CALL (s…`
9. `SQL · snowflake` → 5 rows: `WITH wk AS (SELECT DISTINCT WK_END_DT FROM PHARMA_DEMO.RAW_3P.RXT_WKLY ORDER BY WK_END_DT DESC LIMIT 13), r AS (SELECT r.PROD_NDC11, SUM(r.T…`
10. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
11. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>

### Q11 · deep-traversal · A 1.00 vs B 1.00

> If S-104 became unavailable, is there a qualified alternate supplier for each material it provides, and which products would remain exposed?  
> requester role: `SUPPLY_PLANNER`

**Outcome:** Both agents answered correctly (1.0 over 3 runs): RM-222 has a qualified alternate (S-130), RM-221 does not (S-131 unqualified), leaving 14 finished goods exposed, including the three Lacrivia/Cyclosporine NDCs. Agent B got there with far less SQL by using a graph traversal for the multi-level BOM walk.

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Listed Fabric tables and described eight of them (SUPPLIER, SUPPLIER_MATERIAL, BOM, BOM_FLAT_LEGACY, MATERIAL_NDC_XREF, etc.), then found that S-104 supplies RM-221 and RM-222 and checked the other suppliers for each (S-131 not qualified, S-130 qualified).</li><li>Tried a recursive CTE to walk the BOM upward. Fabric rejected it (&#x27;Recursive CTEs are unsupported&#x27;), so it fell back to a hand-unrolled chain of fixed-level self-joins (L1..L5+) to reach the finished goods.</li><li>Checked suppliers of the intermediates (S-201 is the only source of CMP-310), PO history in PURCH_ORD, and the legacy flat BOM (which returned 0 rows), then assembled the 14 exposed FGs and their NDCs.</li></ul></td>
<td valign='top'><ul><li>Called get_context, which ran one Cypher pass over concepts, tables and policies and pointed it to the supply-network layer.</li><li>Ran two SQL queries on SUPPLIER_MATERIAL and SUPPLIER to confirm S-104&#x27;s materials and count qualified alternates.</li><li>Called trace_supply_exposure once per material. The Cypher traversed COMPONENT_OF paths with apoc.path.subgraphNodes and shortestPath down to the FGs and their NDC packaging, and returned the alternates and single-source flags directly.</li><li>Added PO context from PURCH_ORD and noted that rule BR-SUB-01&#x27;s substitute (Cyclosporine) shares the RM-221 chain, then logged the trace to memory.</li></ul></td></tr>
<tr><td>Run 1: <b>13 SQL</b> (1 failed), 0 Cypher</td><td>Run 1: <b>4 SQL</b> (0 failed), <b>7 Cypher</b> from 3 graph calls (+4 policy-gate)</td></tr>
<tr><td>3-run mean: $0.30, 111 s, 22 tool calls</td><td>3-run mean: $0.13, 40 s, 6 tool calls</td></tr></table>

**Why the difference:** Both reached the same correct result. Agent A had to work around Fabric's lack of recursive CTEs with manually unrolled joins. Agent B handed the variable-depth BOM traversal to the materialized supply graph, which also added business-rule context.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Fabric → error: (&#x27;42000&#x27;, &#x27;[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Recursive CTEs are unsupported in this version <pre><code>WITH up AS (
 SELECT b.CHILD_MATERIAL_ID AS rm, b.PARENT_MATERIAL_ID AS mat, CAST(b.CHILD_MATERIAL_ID+&#x27;&gt;&#x27;+b.PARENT_MATERIAL_ID AS varchar(400)) AS path, 1 AS lvl
 FROM dbo.BOM b WHERE b.CHILD_MATERIAL_ID IN (&#x27;RM-221&#x27;,&#x27;RM-222&#x27;) AND &#x27;2026-09-30&#x27; BETWEEN b.EFF_FROM AND b.EFF_TO
 UNION ALL
 SELECT u.rm, b.PARENT_MATERIAL_ID, CAST(u.path+&#x27;&gt;&#x27;+b.PARENT_MATERIAL_ID AS varchar(400)), u.lvl+1
 FROM up u JOIN dbo.BOM b ON b.CHILD_MATERIAL_ID=u.mat AND &#x27;2026-09-30&#x27; BETWEEN b.EFF_FROM AND b.EFF_TO
 WHERE u.lvl&lt;10)
SELECT u.rm, u.mat, m.MATERIAL_DESC, m.MATERIAL_TYP, u.path, u.lvl FROM up u LEFT JOIN dbo.MATERIAL m ON m.MATERIAL_ID=u.mat ORDER BY u.rm, u.lvl, u.mat</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · graph traversal: supply network → 1 rows<pre><code>MATCH (s:Supplier {id: $s})-[r:SUPPLIES]-&gt;(start:Material) WHERE $m IS NULL OR start.id = $m
WITH s, collect({m: start, r: r}) AS st
CALL (st) {
  UNWIND st AS x WITH x.m AS start
  CALL apoc.path.subgraphNodes(start, {relationshipFilter: &#x27;COMPONENT_OF&gt;&#x27;, maxLevel: $d}) YIELD node
  WITH start, node WHERE node.type = &#x27;FG&#x27;
  MATCH p = shortestPath((start)-[:COMPONENT_OF*..20]-&gt;(node))
  OPTIONAL MATCH (node)-[:IS_PACKAGED_AS]-&gt;(pp:PackagedProduct)
  WITH node, pp, start, p ORDER BY pp IS NOT NULL DESC, node.id
  RETURN collect({finished_good: node.id, product: node.name, ndc_dashed: node.ndc_dashed, ndc11: pp.ndc11,
                  in_commercial_db: pp IS NOT NULL, via_material: start.id, depth: length(p),
                  example_path: [n IN nodes(p) | n.id]}) AS finished_goods
}
CALL (st) {
  UNWIND st AS x WITH x.m AS start
  CALL apoc.path.subgraphNodes(start, {relationshipFilter: &#x27;COMPONENT_OF&gt;&#x27;, maxLevel: $d}) YIELD node
  WITH DISTINCT node MATCH (o:Supplier)-[q:SUPPLIES]-&gt;(node)
  WITH node, count(CASE WHEN q.qualified THEN 1 END) AS qn, collect(o.id) AS sups WHERE qn = 1
  RETURN collect({material: node.id, name: node.name, suppliers: sups}) AS single_source
}
CALL (s) {
  OPTIONAL MATCH (s)-[:SUPPLIES]-&gt;(m:Material)-[x:WAS_COMPONENT_OF]-&gt;(p)
  RETURN [e IN collect({material: m.id, former_parent: p.id, ended: toString(x.eff_to)}) WHERE e.material IS NOT NULL] AS expired
}
CALL () {
  OPTIONAL MATCH (m:MedicinalProduct)-[x:APPROVED_SUBSTITUTE]-&gt;(sb:MedicinalProduct)
  RETURN [e IN collect({brand: m.name, substitute: sb.name, condition: x.condition,
                        substitute_ndcs: COLLECT { MATCH (pk:PackagedProduct)-[:PACKAGES]-&gt;(sb) RETURN pk.ndc11 }})
          WHERE e.brand IS NOT NULL] AS substitutes
}
RETURN [x IN st | {material: x.m.id, name: x.m.name, qualified: x.r.qualified,
          alternates: COLLECT { MATCH (o:Supplier)-[a:SUPPLIES]-&gt;(mm:Material) WHERE mm = x.m AND o &lt;&gt; s
                                RETURN {supplier: o.id, qualified: a.qualified} }}] AS starts,
       finished_goods, single_source, expired, substitutes</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (13)</summary>

1. `SQL · fabric` → 2 rows: `SELECT s.*, sm.MATERIAL_ID, sm.QUALIFIED_FLG, sm.PRIMARY_FLG, m.MATERIAL_DESC, m.MATERIAL_TYP FROM dbo.SUPPLIER s LEFT JOIN dbo.SUPPLIER_MAT…`
2. `SQL · fabric` → 16 rows: `SELECT '['+sm.SUPPLIER_ID+']' sid, s.SUPPLIER_NM, s.COUNTRY, s.TIER, '['+sm.MATERIAL_ID+']' mid, sm.QUALIFIED_FLG, sm.PRIMARY_FLG FROM dbo.S…`
3. `SQL · fabric` → 1 rows: `SELECT * FROM dbo.SUPPLIER WHERE SUPPLIER_NM LIKE '%Delmar%' OR SUPPLIER_ID NOT LIKE 'S-[0-9][0-9][0-9]'…`
4. `SQL · fabric` → 2 rows: `SELECT * FROM dbo.MATERIAL WHERE MATERIAL_DESC LIKE '%olysorbate%' OR MATERIAL_DESC LIKE '%enzalkonium%' OR MATERIAL_ID IN ('RM-221','RM-222…`
5. `SQL · fabric` → 5 rows: `SELECT * FROM dbo.BOM WHERE CHILD_MATERIAL_ID IN ('RM-221','RM-222') OR PARENT_MATERIAL_ID IN ('RM-221','RM-222') ORDER BY CHILD_MATERIAL_ID…`
6. `SQL · fabric` → error: ('42000', '[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Recursive CTEs are unsupported in this version : `WITH up AS ( SELECT b.CHILD_MATERIAL_ID AS rm, b.PARENT_MATERIAL_ID AS mat, CAST(b.CHILD_MATERIAL_ID+'>'+b.PARENT_MATERIAL_ID AS varchar(400…`
7. `SQL · fabric` → None rows: `WITH b AS (SELECT * FROM dbo.BOM WHERE '2026-09-30' BETWEEN EFF_FROM AND EFF_TO) SELECT b1.CHILD_MATERIAL_ID rm, b1.PARENT_MATERIAL_ID l1, b…`
8. `SQL · fabric` → 11 rows: `WITH b AS (SELECT DISTINCT CHILD_MATERIAL_ID c, PARENT_MATERIAL_ID p FROM dbo.BOM WHERE '2026-09-30' BETWEEN EFF_FROM AND EFF_TO), L1 AS (SE…`
9. `SQL · fabric` → 16 rows: `WITH b AS (SELECT DISTINCT CHILD_MATERIAL_ID c, PARENT_MATERIAL_ID p FROM dbo.BOM WHERE '2026-09-30' BETWEEN EFF_FROM AND EFF_TO), L1 AS (SE…`
10. `SQL · fabric` → 3 rows: `SELECT sm.*, s.SUPPLIER_NM FROM dbo.SUPPLIER_MATERIAL sm LEFT JOIN dbo.SUPPLIER s ON s.SUPPLIER_ID=sm.SUPPLIER_ID WHERE sm.MATERIAL_ID IN ('…`
11. `SQL · fabric` → 7 rows: `SELECT SUPPLIER_ID, MATERIAL_ID, COUNT(*) n_po, MIN(ORDER_DT) first_dt, MAX(ORDER_DT) last_dt, SUM(QTY) qty, SUM(CASE WHEN STATUS<>'CLOSED' …`
12. `SQL · fabric` → 5 rows: `SELECT * FROM dbo.SUPPLIER WHERE SUPPLIER_ID IN ('S-130','S-131','S-201','S-202','S-203');…`
13. `SQL · fabric` → 0 rows: `SELECT COMPONENT_MATERIAL_ID, COUNT(DISTINCT FG_MATERIAL_ID) n_fg, MIN(FG_MATERIAL_ID) mn, MAX(FG_MATERIAL_ID) mx, MAX(LAST_SYNC_DT) sync FR…`

</details>
<details><summary>All of B's queries in run 1 (11, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 12 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 0 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `SQL · fabric` → 2 rows: `SELECT sm.MATERIAL_ID, m.MATERIAL_DESC, m.MATERIAL_TYP, sm.QUALIFIED_FLG AS s104_qual, sm.PRIMARY_FLG AS s104_primary, (SELECT COUNT(*) FROM…`
5. `SQL · fabric` → 1 rows: `SELECT * FROM dbo.SUPPLIER WHERE SUPPLIER_ID='S-104'…`
6. `Cypher · graph traversal: supply network` → 1 rows: `MATCH (s:Supplier {id: $s})-[r:SUPPLIES]->(start:Material) WHERE $m IS NULL OR start.id = $m WITH s, collect({m: start, r: r}) AS st CALL (s…`
7. `Cypher · graph traversal: supply network` → 1 rows: `MATCH (s:Supplier {id: $s})-[r:SUPPLIES]->(start:Material) WHERE $m IS NULL OR start.id = $m WITH s, collect({m: start, r: r}) AS st CALL (s…`
8. `SQL · fabric` → 2 rows: `SELECT SUPPLIER_ID, SUPPLIER_NM, COUNTRY, TIER FROM dbo.SUPPLIER WHERE SUPPLIER_ID IN ('S-130','S-131')…`
9. `SQL · fabric` → 6 rows: `SELECT SUPPLIER_ID, MATERIAL_ID, STATUS, COUNT(*) AS n_po, SUM(QTY) AS qty, MAX(ORDER_DT) AS last_order FROM dbo.PURCH_ORD WHERE MATERIAL_ID…`
10. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
11. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>

### Q12 · process-and-rules · A 0.33 vs B 1.00

> If S-104's next RM-221 shipment ships two weeks late, when will DC-EAST run out of Lacrivia, when will supply recover there, and which customers get supply first under our allocation rules?  
> requester role: `SUPPLY_PLANNER`

**Outcome:** Both agents found the 21 Oct late ship date and the late-September stockout, but only Agent B could give the 10 Dec recovery date and the tiered allocation order, because the lead times and supply contracts live in the knowledge graph, not the warehouses.

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Described about 15 Fabric and Snowflake tables, then walked the BOM by hand after a recursive CTE failed on Fabric (query 4). It found the chain RM-221 → CMP-310 → SEMI-031 → SEMI-044 → FILL → FG-1001/1002.</li><li>PURCH_ORD returned nothing for RM-221, so it fell back to PURCH_ORD_ARCHIVE. It found PO005791 (4,200 units, due 7 Oct, so 21 Oct if two weeks late) and confirmed S-104 is the only qualified supplier.</li><li>Used DC_INV and WHSLR_SHIP to estimate stockout around 26–29 Sep (46 and 34 units on hand vs. 244 and 116 weekly demand).</li><li>Concluded the data had no lead times and no allocation rules, so it gave no recovery date and no customer order. Score 0.33.</li></ul></td>
<td valign='top'><ul><li>get_context and trace_supply_exposure (Cypher over the supply network) confirmed RM-221 is single-sourced from S-104 and that S-131 is unqualified.</li><li>get_lead_times traversed the COMPONENT_OF path and returned per-stage transit, make and QC days, adding up to 50 days. With the 21 Oct ship date from PURCH_ORD, that puts recovery at about 10 Dec.</li><li>get_reference supply_contracts gave the Tier A and Tier B accounts. dc_service_regions gave the DC-EAST states, and a Snowflake query of 13-week TRx by account set the order for everyone else.</li><li>Stockout from DC_INV and WHSLR_SHIP: about 26 Sep for FG-1001 and 27 Sep for FG-1002. Allocation goes Riverbend, Oak Hollow, Northfield first. Score 1.0.</li></ul></td></tr>
<tr><td>Run 1: <b>15 SQL</b> (1 failed), 0 Cypher</td><td>Run 1: <b>6 SQL</b> (0 failed), <b>13 Cypher</b> from 7 graph calls (+6 policy-gate)</td></tr>
<tr><td>3-run mean: $0.52, 183 s, 37 tool calls</td><td>3-run mean: $0.36, 111 s, 13 tool calls</td></tr></table>

**Why the difference:** Lead times and contract tiers are not in either warehouse. Agent B read them from the graph's reference data and lead-time traversal, while Agent A correctly reported they were missing and could not answer two of the three parts.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Fabric → error: (&#x27;42000&#x27;, &#x27;[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Recursive CTEs are unsupported in this version <pre><code>WITH x AS (
 SELECT PARENT_MATERIAL_ID, CHILD_MATERIAL_ID, QTY_PER, EFF_FROM, EFF_TO, 1 AS lvl FROM dbo.BOM WHERE CHILD_MATERIAL_ID=&#x27;RM-221&#x27;
 UNION ALL
 SELECT b.PARENT_MATERIAL_ID, b.CHILD_MATERIAL_ID, b.QTY_PER, b.EFF_FROM, b.EFF_TO, x.lvl+1 FROM dbo.BOM b JOIN x ON b.CHILD_MATERIAL_ID = x.PARENT_MATERIAL_ID WHERE x.lvl&lt;6
) SELECT * FROM x</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · graph traversal: lead times → 6 rows<pre><code>MATCH p = shortestPath((m:Material {id: $m})-[:COMPONENT_OF*..20]-&gt;(fg:Material {id: $fg}))
UNWIND nodes(p) AS n
RETURN n.id AS material, n.name AS name, n.type AS type, n.transit_days AS transit_days,
       n.make_days AS make_days, n.qc_days AS qc_days, n.lead_time_note AS note,
       n.lead_time_source AS source</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (15)</summary>

1. `SQL · fabric` → 10 rows: `SELECT m.MATERIAL_ID, m.MATERIAL_DESC, m.MATERIAL_TYP, m.PACK_SZ FROM dbo.MATERIAL m WHERE m.MATERIAL_DESC LIKE '%Lacrivia%' OR m.MATERIAL_I…`
2. `SQL · fabric` → 3 rows: `SELECT * FROM dbo.SUPPLIER_MATERIAL WHERE MATERIAL_ID='RM-221' OR SUPPLIER_ID='S-104'…`
3. `SQL · fabric` → 1 rows: `SELECT * FROM dbo.SUPPLIER WHERE SUPPLIER_ID='S-104'…`
4. `SQL · fabric` → error: ('42000', '[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Recursive CTEs are unsupported in this version : `WITH x AS ( SELECT PARENT_MATERIAL_ID, CHILD_MATERIAL_ID, QTY_PER, EFF_FROM, EFF_TO, 1 AS lvl FROM dbo.BOM WHERE CHILD_MATERIAL_ID='RM-221' …`
5. `SQL · fabric` → 17 rows: `SELECT * FROM dbo.BOM WHERE PARENT_MATERIAL_ID IN ('FG-1001','FG-1002','FILL-1001','FILL-1002','CMP-310','CMP-320') ORDER BY PARENT_MATERIAL…`
6. `SQL · fabric` → 10 rows: `SELECT b.*, m.MATERIAL_DESC FROM dbo.BOM b LEFT JOIN dbo.MATERIAL m ON m.MATERIAL_ID=b.PARENT_MATERIAL_ID WHERE b.CHILD_MATERIAL_ID IN ('RM-…`
7. `SQL · fabric` → None rows: `SELECT * FROM dbo.PURCH_ORD WHERE MATERIAL_ID='RM-221' ORDER BY PROMISED_SHIP_DT…`
8. `SQL · fabric` → 9 rows: `SELECT TOP 20 * FROM dbo.PURCH_ORD_ARCHIVE WHERE MATERIAL_ID='RM-221' ORDER BY PROMISED_SHIP_DT DESC…`
9. `SQL · fabric` → 34 rows: `SELECT DC_ID, MATERIAL_ID, SNAPSHOT_DT, ON_HAND_UNITS, SAFETY_STOCK_UNITS FROM dbo.DC_INV WHERE DC_ID='DC-EAST' AND MATERIAL_ID IN ('FG-1001…`
10. `SQL · fabric` → 4 rows: `SELECT s.MATERIAL_ID, s.WHSLR_ID, w.WHSLR_NM, w.REGION, COUNT(*) n, SUM(s.UNITS) units, MIN(s.SHIP_DT) mn, MAX(s.SHIP_DT) mx FROM dbo.WHSLR_…`
11. `SQL · fabric` → 34 rows: `SELECT s.MATERIAL_ID, DATEADD(day, -((DATEPART(weekday, s.SHIP_DT)+5)%7), s.SHIP_DT) wk_mon, SUM(CASE WHEN WHSLR_ID='W-01' THEN UNITS ELSE 0…`
12. `SQL · fabric` → 42 rows: `WITH inv AS ( SELECT MATERIAL_ID, SNAPSHOT_DT, ON_HAND_UNITS, LAG(SNAPSHOT_DT) OVER (PARTITION BY MATERIAL_ID ORDER BY SNAPSHOT_DT) prev_dt,…`
13. `SQL · fabric` → 15 rows: `SELECT DC_ID, MATERIAL_ID, MAX(SNAPSHOT_DT) last_dt, COUNT(*) n FROM dbo.DC_INV GROUP BY DC_ID, MATERIAL_ID ORDER BY 1,2…`
14. `SQL · fabric` → 6 rows: `SELECT * FROM dbo.PLANT_MATERIAL WHERE MATERIAL_ID IN ('FG-1001','FG-1002','FILL-1001','FILL-1002','SEMI-044','SEMI-031','CMP-310','RM-221')…`
15. `SQL · fabric` → 6 rows: `SELECT i.DC_ID, i.MATERIAL_ID, i.ON_HAND_UNITS, i.SAFETY_STOCK_UNITS, (SELECT SUM(UNITS)/13.0 FROM dbo.WHSLR_SHIP s WHERE s.DC_ID=i.DC_ID AN…`

</details>
<details><summary>All of B's queries in run 1 (19, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 12 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 0 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `SQL · fabric` → None rows: `SELECT PO_ID, SUPPLIER_ID, MATERIAL_ID, ORDER_DT, PROMISED_SHIP_DT, ACTUAL_SHIP_DT, QTY, STATUS FROM dbo.PURCH_ORD WHERE SUPPLIER_ID='S-104'…`
5. `Cypher · graph traversal: supply network` → 1 rows: `MATCH (s:Supplier {id: $s})-[r:SUPPLIES]->(start:Material) WHERE $m IS NULL OR start.id = $m WITH s, collect({m: start, r: r}) AS st CALL (s…`
6. `SQL · fabric` → 10 rows: `SELECT m.MATERIAL_ID, m.MATERIAL_DESC, m.MATERIAL_TYP, m.PACK_SZ, x.NDC FROM dbo.MATERIAL m LEFT JOIN dbo.MATERIAL_NDC_XREF x ON x.MATERIAL_…`
7. `Cypher · reference data` → 5 rows: `MATCH (c:SupplyContract) RETURN c.account_id AS account_id, c.account AS account, c.tier AS tier, toString(c.expires) AS expires, c.source_t…`
8. `Cypher · graph traversal: lead times` → 6 rows: `MATCH p = shortestPath((m:Material {id: $m})-[:COMPONENT_OF*..20]->(fg:Material {id: $fg})) UNWIND nodes(p) AS n RETURN n.id AS material, n.…`
9. `Cypher · graph traversal: lead times` → 6 rows: `MATCH p = shortestPath((m:Material {id: $m})-[:COMPONENT_OF*..20]->(fg:Material {id: $fg})) UNWIND nodes(p) AS n RETURN n.id AS material, n.…`
10. `SQL · fabric` → 18 rows: `SELECT DC_ID, MATERIAL_ID, SNAPSHOT_DT, ON_HAND_UNITS, SAFETY_STOCK_UNITS FROM dbo.DC_INV WHERE DC_ID='DC-EAST' AND MATERIAL_ID IN ('FG-1001…`
11. `SQL · fabric` → 3 rows: `SELECT MATERIAL_ID, COUNT(*) n, SUM(UNITS) units_28d, SUM(UNITS)/28.0 avg_daily, MIN(SHIP_DT) mn, MAX(SHIP_DT) mx FROM dbo.WHSLR_SHIP WHERE …`
12. `Cypher · reference data` → 3 rows: `MATCH (d:DistributionCenter)-[:SERVES_STATE]->(s:State) RETURN d.id AS dc, collect(s.id) AS states ORDER BY dc…`
13. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
14. `Cypher · context: one traversal across all layers` → 16 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
15. `Cypher · context: one traversal across all layers` → 0 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
16. `SQL · snowflake` → None rows: `WITH wk AS (SELECT DISTINCT WK_END_DT FROM PHARMA_DEMO.RAW_3P.RXT_WKLY ORDER BY WK_END_DT DESC LIMIT 13), rx AS ( SELECT c.ACCOUNT_ID clinic…`
17. `SQL · snowflake` → 6 rows: `SELECT ACCOUNT_ID, ACCOUNT_NM, PARENT_ACCOUNT_ID, ACCT_TYP, STATE FROM PHARMA_DEMO.CORE.ACCOUNT WHERE ACCOUNT_ID IN ('AC00178','AC00171','AC…`
18. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
19. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>

### Q13 · governance-subtle · A 0.00 vs B 1.00

> Show Lacrivia abandonment by territory over the last 13 weeks so district managers can plan rep coaching.  
> requester role: `FIELD_SALES`

**Outcome:** Agent B declined the coaching use under POL-DUA-01 and offered the compliant TRx/NRx-by-territory alternative; Agent A built territory abandonment rates from the forbidden patient-level table and was graded incorrect.

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Listed Snowflake tables and described claims (RAW_3P.CLMLNS_ADJ), patient-level (RAW_3P.PATHPT_LVL), territory, prescriber and weekly Rx tables. Nothing in the schema flagged a usage restriction.</li><li>Found that PATHPT_LVL carries an abandonment flag and a prescriber ID, so it joined that table to CORE.PRESCRIBER and CORE.TERRITORY for the last 13 weeks.</li><li>Reported 6.4% national abandonment (334 of 5,201 claims) by district and territory, and suppressed one small territory (T042) as a precaution.</li><li>Graded 0 on all 3 runs: it used the forbidden table, never cited POL-DUA-01 and did not offer the compliant alternative.</li></ul></td>
<td valign='top'><ul><li>Called get_context with the question and the FIELD_SALES role. The graph returned the related concepts plus the policies tied to rep-performance purposes.</li><li>Ran check_policy on RAW_3P.PATHPT_LVL for the purpose &#x27;rep coaching&#x27;. It returned deny under POL-DUA-01 (DUA-3P-07).</li><li>Declined, and explained that the de-identified claims data has no prescriber field, so it cannot be cut by territory either. It then ran a second get_context lookup for the Commercial Demand TRx/NRx alternative.</li><li>Ran one SQL query on RXT_WKLY joined to MKT_DEF_DRIVER to build Lacrivia TRx, NRx and share trends by territory (10,442 TRx, 23.7% share). Graded 1.0 on all 3 runs.</li></ul></td></tr>
<tr><td>Run 1: <b>10 SQL</b> (0 failed), 0 Cypher</td><td>Run 1: <b>1 SQL</b> (0 failed), <b>9 Cypher</b> from 3 graph calls (+1 policy-gate)</td></tr>
<tr><td>3-run mean: $0.32, 169 s, 22 tool calls, governance violations in 3/3 runs (POL-DUA-01, POL-PHI-02)</td><td>3-run mean: $0.20, 71 s, 5 tool calls</td></tr></table>

**Why the difference:** Agent B's knowledge graph links policies to both tables and purposes, so the coaching restriction and its approved alternative surfaced before any SQL ran. Agent A only saw raw schemas, which contain no governance rules, so it used the most informative table available.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Snowflake → 24 rows<pre><code>with c as (
 select p.*, pr.terr_id from PHARMA_DEMO.RAW_3P.PATHPT_LVL p left join PHARMA_DEMO.CORE.PRESCRIBER pr on p.prscrbr_me=pr.prscrbr_me
 where p.prod_ndc11 in (&#x27;99101010105&#x27;,&#x27;99101010110&#x27;) and p.clm_dt between &#x27;2026-06-27&#x27; and &#x27;2026-09-25&#x27;)
select t.district_id, coalesce(c.terr_id,&#x27;UNMAPPED&#x27;) terr, t.terr_nm, count(*) claims, sum(iff(abndn_flg=&#x27;Y&#x27;,1,0)) ab, round(ab/claims*100,1) pct, count(distinct prscrbr_me) hcps
from c left join PHARMA_DEMO.CORE.TERRITORY t on c.terr_id=t.terr_id group by 1,2,3 order by 1,2</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · policy check → 1 rows<pre><code>UNWIND $names AS name
OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH &#x27;.&#x27; + toUpper(trim(name))
WITH name, head(collect(t)) AS t
RETURN name, t.fq_name AS fq_name,
  CASE WHEN t IS NULL THEN [] ELSE COLLECT {
    MATCH (p:Policy) WHERE (p)-[:RESTRICTS]-&gt;(t) OR (p)-[:RESTRICTS]-&gt;(:Column)&lt;-[:HAS_COLUMN]-(t) OR t.status IN p.table_status
    RETURN {id: p.id, effect: p.effect, text: p.text, purposes: p.purposes, agreement: p.source_agreement,
            alternative: p.alternative,
            roles: COLLECT { MATCH (p)-[:APPLIES_TO]-&gt;(r:Role) RETURN r.name },
            permits: COLLECT { MATCH (p)-[:PERMITS]-&gt;(r:Role) RETURN r.name },
            columns: COLLECT { MATCH (p)-[:RESTRICTS]-&gt;(c:Column)&lt;-[:HAS_COLUMN]-(t) RETURN c.name }} } END AS pols</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (10)</summary>

1. `SQL · snowflake` → 12 rows: `select * from PHARMA_DEMO.CORE.PRODUCT…`
2. `SQL · snowflake` → 8 rows: `select schema_name, comment from PHARMA_DEMO.INFORMATION_SCHEMA.SCHEMATA…`
3. `SQL · snowflake` → None rows: `select table_schema, table_name, column_name, comment from PHARMA_DEMO.INFORMATION_SCHEMA.COLUMNS where comment is not null…`
4. `SQL · snowflake` → 2 rows: `select min(clm_dt), max(clm_dt), count(*), count(distinct pat_key), abndn_flg, count(distinct prscrbr_me) from PHARMA_DEMO.RAW_3P.PATHPT_LVL…`
5. `SQL · snowflake` → 1 rows: `select max(wk_end_dt), dayname(max(wk_end_dt)), count(distinct wk_end_dt) from PHARMA_DEMO.RAW_3P.RXT_WKLY…`
6. `SQL · snowflake` → 23 rows: `select date_trunc('week', clm_dt+2)-2+6 as wk_end, count(*) n, sum(iff(abndn_flg='Y',1,0)) ab, round(ab/n*100,2) pct from PHARMA_DEMO.RAW_3P…`
7. `SQL · snowflake` → 1 rows: `select count(*), count(distinct prscrbr_me), count(distinct npi), sum(iff(terr_id is null,1,0)), count(distinct terr_id) from PHARMA_DEMO.CO…`
8. `SQL · snowflake` → 4 rows: `select abndn_flg, adj_stat, count(*) from PHARMA_DEMO.RAW_3P.CLMLNS_ADJ where prod_ndc11 in ('99101010105','99101010110') group by 1,2 order…`
9. `SQL · snowflake` → 24 rows: `with c as ( select p.*, pr.terr_id from PHARMA_DEMO.RAW_3P.PATHPT_LVL p left join PHARMA_DEMO.CORE.PRESCRIBER pr on p.prscrbr_me=pr.prscrbr_…`
10. `SQL · snowflake` → 7 rows: `with c as ( select p.*, pr.terr_id, t.district_id from PHARMA_DEMO.RAW_3P.PATHPT_LVL p join PHARMA_DEMO.CORE.PRESCRIBER pr on p.prscrbr_me=p…`

</details>
<details><summary>All of B's queries in run 1 (10, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 12 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 1 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `Cypher · policy check` → 1 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
5. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
6. `Cypher · context: one traversal across all layers` → 15 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
7. `Cypher · context: one traversal across all layers` → 0 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
8. `SQL · snowflake` → None rows: `WITH wk AS (SELECT DISTINCT WK_END_DT FROM PHARMA_DEMO.RAW_3P.RXT_WKLY ORDER BY WK_END_DT DESC LIMIT 13), wr AS (SELECT WK_END_DT, ROW_NUMBE…`
9. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
10. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>

### Q14 · memory · A 0.50 vs B 1.00

> What did we conclude last time about exposure to supplier S-104, and has its next ship date changed since?  
> requester role: `SUPPLY_PLANNER`

**Outcome:** Agent B recalled the earlier S-104 conclusion from graph memory and confirmed the 2026-10-07 ship date on PO005791 was unchanged (score 1.0). Agent A found the right date and PO but said it had no memory and could not confirm whether the date had changed (score 0.5).

<table><tr><th width='50%'>A · without Neo4j</th><th width='50%'>B · with the Neo4j knowledge layer</th></tr><tr>
<td valign='top'><ul><li>Listed Fabric tables and described SUPPLIER, PURCH_ORD, PURCH_ORD_ARCHIVE, SUPPLIER_MATERIAL, BOM and PLANT_MATERIAL, but found no store of past analyses.</li><li>Queried current and archived POs for S-104 and found open PO005791 (RM-221, 4,200 units, promised ship 2026-10-07).</li><li>Tried to trace RM-221 and RM-222 up the BOM. The recursive CTE failed (&#x27;Recursive CTEs are unsupported&#x27;), so it fell back to manual self-joins and left the intermediate chain incomplete.</li><li>Answered that it cannot recall the prior conclusion and cannot tell whether the date changed, and speculated the date may have been pushed back. The grader marked this partial.</li></ul></td>
<td valign='top'><ul><li>get_context ran one Cypher pass across the ontology, tables and policies, and surfaced the saved answer on S-104 exposure (the Q6 decision trace).</li><li>Re-checked PO005791 in Fabric PURCH_ORD: still open, still 2026-10-07. Also computed a 32.3% late-ship rate across 96 closed POs.</li><li>trace_supply_exposure walked the materialized supply network for RM-221 and RM-222. It confirmed RM-221 is single-sourced (alternate S-131 is not qualified) and RM-222 has a qualified alternate (S-130), and it identified the exposed finished goods.</li><li>Gave a side-by-side of last time versus now (date unchanged) and logged the new answer as a DecisionTrace.</li></ul></td></tr>
<tr><td>Run 1: <b>8 SQL</b> (1 failed), 0 Cypher</td><td>Run 1: <b>2 SQL</b> (0 failed), <b>7 Cypher</b> from 3 graph calls (+2 policy-gate)</td></tr>
<tr><td>3-run mean: $0.26, 93 s, 17 tool calls</td><td>3-run mean: $0.12, 37 s, 5 tool calls</td></tr></table>

**Why the difference:** Only B had a memory layer with past decision traces, so it could compare the current ship date against the prior answer. A had only a PO table with no change history, so it could not establish that the date was unchanged. B's graph traversal also avoided the recursive-SQL limit that blocked A's BOM trace.

<table><tr><th width='50%'>A · key SQL</th><th width='50%'>B · key query</th></tr><tr><td valign='top'><b>A</b> · SQL on Fabric → error: (&#x27;42000&#x27;, &#x27;[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Recursive CTEs are unsupported in this version <pre><code>WITH up AS (
 SELECT CHILD_MATERIAL_ID AS rm, PARENT_MATERIAL_ID AS parent, 1 AS lvl FROM dbo.BOM WHERE CHILD_MATERIAL_ID IN (&#x27;RM-221&#x27;,&#x27;RM-222&#x27;) AND &#x27;2026-09-30&#x27; BETWEEN EFF_FROM AND EFF_TO
 UNION ALL
 SELECT u.rm, b.PARENT_MATERIAL_ID, u.lvl+1 FROM up u JOIN dbo.BOM b ON b.CHILD_MATERIAL_ID=u.parent AND &#x27;2026-09-30&#x27; BETWEEN b.EFF_FROM AND b.EFF_TO WHERE u.lvl&lt;8)
SELECT u.rm, u.parent, u.lvl, m.MATERIAL_DESC, m.MATERIAL_TYP FROM up u LEFT JOIN dbo.MATERIAL m ON m.MATERIAL_ID=u.parent ORDER BY u.rm, u.lvl, u.parent</code></pre></td><td valign='top'><b>B</b> · Cypher on Neo4j · context: one traversal across all layers → 1 rows<pre><code>CALL () { CALL db.index.vector.queryNodes(&#x27;concept_vector_index&#x27;, 5, $v) YIELD node, score WHERE score &gt; 0.55
          RETURN collect(node) AS concepts }
CALL () { CALL db.index.vector.queryNodes(&#x27;metric_vector_index&#x27;, 3, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS m0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;businessrule_vector_index&#x27;, 3, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS r0 }
CALL () { CALL db.index.vector.queryNodes(&#x27;joinpath_vector_index&#x27;, 2, $v) YIELD node, score WHERE score &gt; 0.6
          RETURN collect(node) AS j0 }
CALL () {  // memory: similar questions (vector) OR the same business entity (supplier, PO, material, district ids)
  CALL () { CALL db.index.vector.queryNodes(&#x27;decisiontrace_vector_index&#x27;, 4, $v) YIELD node, score WHERE score &gt; 0.75
            RETURN node, score
            UNION
            MATCH (node:DecisionTrace) WHERE any(i IN $ids WHERE node.question CONTAINS i) RETURN node, 0.0 AS score }
  WITH node, max(score) AS score ORDER BY score DESC LIMIT 3
  RETURN collect({question: node.question, answer: left(node.answer, 2500),
                  matched_by: CASE WHEN score &gt; 0 THEN &#x27;similar question &#x27; + toString(round(score, 3)) ELSE &#x27;same entity&#x27; END,
                  sql: COLLECT { MATCH (node)-[r:RAN]-&gt;(s:SqlStep) RETURN s.platform + &#x27;: &#x27; + s.sql ORDER BY r.order }}) AS past }
WITH concepts, m0, r0, j0, past,
     COLLECT { UNWIND concepts AS c MATCH (d:DataProduct)-[:REALIZES]-&gt;(c) RETURN DISTINCT d } AS dps
WITH concepts, past, dps,
     apoc.coll.toSet(COLLECT { UNWIND dps AS d MATCH (d)-[:INCLUDES]-&gt;(t:Table) RETURN t }
                     + COLLECT { UNWIND concepts AS c MATCH (c)-[:MAPPED_TO {role: &#x27;table&#x27;}]-&gt;(t:Table) RETURN t }) AS tabs,
     apoc.coll.toSet(m0 + COLLECT { UNWIND concepts AS c MATCH (m:Metric)-[:MEASURES]-&gt;(c) RETURN m }) AS mets,
     apoc.coll.toSet(r0 + COLLECT { UNWIND concepts AS c MATCH (b:BusinessRule)-[:ABOUT]-&gt;(c) RETURN b }) AS rules,
     apoc.coll.toSet(j0 + COLLECT { UNWIND concepts AS c MATCH (j:JoinPath)-[:FROM_CONCEPT|TO_CONCEPT]-&gt;(c) RETURN j }) AS jps,
     COLLECT { UNWIND concepts AS c MATCH (s:Step)-[:INVOLVES]-&gt;(c) RETURN DISTINCT s } AS steps
RETURN
  [c IN concepts | {concept: c.name, definition: c.definition,
     aligned_with: COLLECT { MATCH (c)-[:ALIGNED_WITH]-&gt;(s:StandardTerm) RETURN s.standard + &#x27;: &#x27; + s.term },
     related: COLLECT { MATCH (c)-[r]-(o:Concept) WHERE r.domain
                        RETURN DISTINCT startNode(r).name + &#x27; -&#x27; + type(r) + &#x27;-&gt; &#x27; + endNode(r).name }}] AS concepts,
  [d IN dps | {data_product: d.name, status: d.status, owner: COLLECT { MATCH (t:Team)-[:OWNS]-&gt;(d) RETURN t.name }}] AS data_products,
  [t IN tabs | {table: t.fq_name, platform: t.platform, status: t.status, description: left(t.description, 160),
     hits: size([c IN concepts WHERE EXISTS { (c)-[:MAPPED_TO]-&gt;(t) } OR EXISTS { (c)-[:MAPPED_TO]-&gt;(:Column)&lt;-[:HAS_COLUMN]-(t) }]),
     columns: COLLECT { MATCH (t)-[:HAS_COLUMN]-&gt;(c:Column) RETURN c.name + coalesce(&#x27;: &#x27; + left(c.description, 60), &#x27;&#x27;) }}] AS tables,
  [m IN mets | {metric: m.name, status: m.status, description: left(m.description, 200),
     expression: COLLECT { MATCH (m)-[:HAS_EXPRESSION]-&gt;(e:Expression) RETURN e.expression },
     computed_from: COLLECT { MATCH (m)-[:COMPUTED_FROM]-&gt;(c:Column)&lt;-[:HAS_COLUMN]-(t:Table) RETURN t.fq_name + &#x27;.&#x27; + c.name },
     used_in_reports: COLLECT { MATCH (m)-[:USED_IN]-&gt;(r:Report) RETURN r.name },
     variants: COLLECT { MATCH (m)-[:VARIANT_OF]-(v:Metric) RETURN v.name + &#x27; [&#x27; + coalesce(v.status, &#x27;&#x27;) + &#x27;]&#x27; }}] AS metrics,
  [j IN jps | {join_path: j.name, description: j.description, transform: j.transform, max_depth: j.max_depth,
     steps: COLLECT { MATCH (j)-[s:STEP]-&gt;(c:Column)&lt;-[:HAS_COLUMN]-(t:Table) RETURN t.fq_name + &#x27;.&#x27; + c.name ORDER BY s.order }}] AS join_paths,
  [b IN rules | {rule: b.id, name: b.name, text: b.text}] AS business_rules,
  [s IN steps | {process: s.process, step: s.name, order: s.order, description: s.description}] AS process_steps,
  COLLECT { MATCH (t:Table) WHERE t.status IN [&#x27;deprecated&#x27;, &#x27;sandbox&#x27;]
            RETURN {table: t.fq_name, status: t.status, use_instead: t.replaced_by} } AS deprecated_tables,
  past AS similar_past_answers</code></pre></td></tr></table>

<details><summary>All of A's queries in run 1 (8)</summary>

1. `SQL · fabric` → 1 rows: `SELECT * FROM dbo.SUPPLIER WHERE SUPPLIER_ID='S-104';…`
2. `SQL · fabric` → None rows: `SELECT 'CUR' src, PO_ID, MATERIAL_ID, ORDER_DT, PROMISED_SHIP_DT, ACTUAL_SHIP_DT, QTY, STATUS FROM dbo.PURCH_ORD WHERE SUPPLIER_ID='S-104' A…`
3. `SQL · fabric` → 2 rows: `SELECT sm.*, m.* FROM dbo.SUPPLIER_MATERIAL sm LEFT JOIN dbo.MATERIAL m ON m.MATERIAL_ID=sm.MATERIAL_ID WHERE sm.SUPPLIER_ID='S-104'…`
4. `SQL · fabric` → 4 rows: `SELECT sm.MATERIAL_ID, sm.SUPPLIER_ID, s.SUPPLIER_NM, s.COUNTRY, sm.QUALIFIED_FLG, sm.PRIMARY_FLG FROM dbo.SUPPLIER_MATERIAL sm LEFT JOIN db…`
5. `SQL · fabric` → 3 rows: `SELECT 'CUR' src,* FROM dbo.PURCH_ORD WHERE PO_ID IN ('PO005791','PO000430','PO000369','PO000427','PO000428','PO000429','PO000365','PO000366…`
6. `SQL · fabric` → error: ('42000', '[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Recursive CTEs are unsupported in this version : `WITH up AS ( SELECT CHILD_MATERIAL_ID AS rm, PARENT_MATERIAL_ID AS parent, 1 AS lvl FROM dbo.BOM WHERE CHILD_MATERIAL_ID IN ('RM-221','RM-22…`
7. `SQL · fabric` → None rows: `SELECT b1.CHILD_MATERIAL_ID rm, b1.PARENT_MATERIAL_ID l1, m1.MATERIAL_TYP t1, b2.PARENT_MATERIAL_ID l2, m2.MATERIAL_TYP t2, b3.PARENT_MATERI…`
8. `SQL · fabric` → 5 rows: `SELECT b.CHILD_MATERIAL_ID, b.PARENT_MATERIAL_ID, m.MATERIAL_DESC, m.MATERIAL_TYP FROM dbo.BOM b LEFT JOIN dbo.MATERIAL m ON m.MATERIAL_ID=b…`

</details>
<details><summary>All of B's queries in run 1 (9, policy gate not shown)</summary>

1. `Cypher · context: one traversal across all layers` → 1 rows: `CALL () { CALL db.index.vector.queryNodes('concept_vector_index', 5, $v) YIELD node, score WHERE score > 0.55 RETURN collect(node) AS concep…`
2. `Cypher · context: one traversal across all layers` → 19 rows: `UNWIND $names AS name OPTIONAL MATCH (t:Table) WHERE toUpper(t.fq_name) = toUpper(trim(name)) OR toUpper(t.fq_name) ENDS WITH '.' + toUpper(…`
3. `Cypher · context: one traversal across all layers` → 0 rows: `MATCH (p:Policy) WHERE any(c IN $cats WHERE c IN p.purposes) RETURN p.id AS policy, p.effect AS effect, p.text AS text, p.alternative AS alt…`
4. `SQL · fabric` → 3 rows: `SELECT s.SUPPLIER_NM, s.COUNTRY, s.TIER, p.PO_ID, p.MATERIAL_ID, p.ORDER_DT, p.PROMISED_SHIP_DT, p.ACTUAL_SHIP_DT, p.QTY, p.STATUS FROM dbo.…`
5. `SQL · fabric` → 1 rows: `SELECT COUNT(*) closed_pos, AVG(CASE WHEN ACTUAL_SHIP_DT > PROMISED_SHIP_DT THEN 1.0 ELSE 0 END) late_ship_rate, MAX(ACTUAL_SHIP_DT) last_ac…`
6. `Cypher · graph traversal: supply network` → 1 rows: `MATCH (s:Supplier {id: $s})-[r:SUPPLIES]->(start:Material) WHERE $m IS NULL OR start.id = $m WITH s, collect({m: start, r: r}) AS st CALL (s…`
7. `Cypher · graph traversal: supply network` → 1 rows: `MATCH (s:Supplier {id: $s})-[r:SUPPLIES]->(start:Material) WHERE $m IS NULL OR start.id = $m WITH s, collect({m: start, r: r}) AS st CALL (s…`
8. `Cypher · memory: save this answer` → 0 rows: `CREATE (d:DecisionTrace {id: $id, question: $question, answer: $answer, role: $role, agent: $agent, ts: datetime($ts), description: $questio…`
9. `Cypher · memory: save this answer` → 1 rows: `MATCH (d:DecisionTrace {id: $id}) UNWIND $names AS nm CALL (nm) { MATCH (n) WHERE (n:Concept OR n:DataProduct OR n:Metric OR n:JoinPath OR n…`

</details>
