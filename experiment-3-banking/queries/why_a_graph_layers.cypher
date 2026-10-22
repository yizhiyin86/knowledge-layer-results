// One traversal across the layers, from an agent's answer (memory) to the data
MATCH (e:LegalEntity {id: 'LE-10001'})<-[:ABOUT]-(t:DecisionTrace)
WHERE t.question STARTS WITH 'After Halvorsen'                        // B's answer to the downgrade question
WITH e, t ORDER BY t.ts DESC LIMIT 1
MATCH p1 = (t)-[:USED]->(:BusinessRule {id: 'BR-DLA-01'})            // L6 -> L1: the approval rule it used
           -[:ABOUT]->(c:Concept {name: 'InternalRiskRating'})        //       -> L2: what the rule is about
MATCH p2 = (:Process)-[:HAS_STEP]->(:Step {name: 'Assess'})-[:INVOLVES]->(c)   // L1: its process step
MATCH p3 = (c)<-[:REALIZES]-(:DataProduct)-[:INCLUDES]->(:Table {name: 'RISK_RATING'})  // L3 -> L4: authoritative table
           <-[:HAS_TABLE]-(:Schema)<-[:HAS_SCHEMA]-(:Database)        //       -> its system
MATCH p4 = (t)-[:USED]->(:Metric {name: 'group_exposure'})-[:MEASURES]->(:Concept)  // L6 -> L3: metric it used
MATCH p5 = (t)-[:ABOUT]->(e)-[:RATED {agency: 'AGY1'}]->(:RatingGrade)
           -[:MAPS_TO_INTERNAL]->(:RiskGrade)-[:INSTANCE_OF]->(c)     // data: CCC+ -> internal grade 8
RETURN p1, p2, p3, p4, p5
