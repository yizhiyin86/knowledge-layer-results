# Figures

Screenshots from the demo app's Execution tab (code repository, `execution-pattern` branch), replicate 3 of the
execution benchmark `20261007T1700`.

| File | What it shows |
|---|---|
| `exec_timeline_T1.png` | Task T1, key steps only: Agent A (left) and Agent B (right). Each step shows the process task it serves, the tool call, the knowledge layer's gate decision (B only) and the result. |
| `exec_playbooks.png` | The playbook proposed by B's T6 run (archived) and the reviewer-corrected version that superseded it, with its confidence after reuse in T7. |
| `exec_badges.png` | The two registered agent badges as stored in the graph. |
| `exec_trace_graph.png` | An execution trace in Neo4j and what it links to: agent, tools, data products, process tasks, policies, playbooks. |
