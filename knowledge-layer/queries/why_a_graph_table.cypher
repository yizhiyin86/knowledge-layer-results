// One traversal: from a process step to everything an agent needs before it acts.
// Task → Concept → authoritative Table → Tool (callable?) → Policy & badge (may this agent?) → approved Playbook
MATCH (agent:Agent {name: 'Supply Response Agent'})
MATCH (:BusinessProcess {name: 'Supply Disruption Response'})
      -[:HAS_ACTIVITIES]->(step:BusinessActivity {name: 'Assess exposure'})
      -[:HAS_TASKS]->(task:BusinessTask)-[:READS_DATA]->(product:DataProduct)
      -[:REALIZES]->(concept:Concept {name: 'Account'})                      // what "customer" means (BR-CUST-01)
MATCH (product)-[:INCLUDES]->(tbl:Table {status: 'ratified'})<-[:MAPPED_TO]-(concept)   // authoritative only
MATCH (tbl)<-[:HAS_TABLE]-(:Schema)<-[:DEFINES_SCHEMA]-(system:SoftwareApplication)
      <-[:WRAPS]-(tool:Tool)<-[:USES_TOOL]-(task)                           // a tool this task uses that reaches it
WITH agent, step, task, concept, product, tbl, system, tool
OPTIONAL MATCH (playbook:KnowledgeAsset {status: 'approved'})-[:APPLIES_TO]->(:BusinessTask)<-[:HAS_TASKS]-(step)
WHERE playbook.confidence >= agent.minTrust                                  // only what this agent may trust
RETURN step.name + ' › ' + task.name                                          AS task,
       concept.name                                                           AS concept,
       tbl.fq_name                                                            AS authoritative_table,
       tool.name + ' (' + tool.status + ')'                                   AS tool,
       system.name                                                            AS system,
       EXISTS { (agent)-[:MAY_USE]->(tool) }
         AND apoc.coll.indexOf(['Public','Internal','Confidential','Restricted'], product.sensitivity)
          <= apoc.coll.indexOf(['Public','Internal','Confidential','Restricted'], agent.maxDataSensitivity)
                                                                              AS agent_may_use_it,
       COLLECT { MATCH (r)-[:GOVERNS]->(task) RETURN r.id }
         + COLLECT { MATCH (p:Policy)-[:RESTRICTS]->(tbl) RETURN p.id }       AS rules_and_policies,
       collect(DISTINCT playbook.name + ' (confidence ' + toString(playbook.confidence) + ')') AS approved_playbooks
