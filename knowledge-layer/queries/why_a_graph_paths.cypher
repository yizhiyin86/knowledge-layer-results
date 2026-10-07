// Same traversal, returned as paths for Neo4j Browser / Bloom (draws the chain)
MATCH taskPath = (:BusinessProcess {name: 'Supply Disruption Response'})-[:HAS_ACTIVITIES]->(step:BusinessActivity {name: 'Assess exposure'})
                 -[:HAS_TASKS]->(task:BusinessTask {id: 'SDR-1.3'})-[:READS_DATA]->(product:DataProduct)-[:REALIZES]->(concept:Concept {name: 'Account'})
MATCH tablePath = (product)-[:INCLUDES]->(tbl:Table {status: 'ratified'})<-[:MAPPED_TO]-(concept)
MATCH toolPath = (tbl)<-[:HAS_TABLE]-(:Schema)<-[:DEFINES_SCHEMA]-(:SoftwareApplication)<-[:WRAPS]-(tool:Tool)<-[:USES_TOOL]-(task)
MATCH badgePath = (:Agent {name: 'Supply Response Agent'})-[:MAY_USE]->(tool)
MATCH rulePath = (:BusinessRule)-[:GOVERNS]->(task)
MATCH playbookPath = (:KnowledgeAsset {status: 'approved'})-[:APPLIES_TO]->(:BusinessTask)<-[:HAS_TASKS]-(step)
RETURN taskPath, tablePath, toolPath, badgePath, rulePath, playbookPath
