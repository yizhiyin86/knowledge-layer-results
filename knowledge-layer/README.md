# Knowledge layer: what is in the graph

Counts read from the two Neo4j Aura instances on 2026-10-07 (read-only queries). The conversation instance serves the code repository's main branch; the execution instance serves the execution-pattern branch (same build plus the execution layers, and the execution traces and playbooks left by the last benchmark replicate).

| | Conversation instance (main) | Execution instance (execution-pattern) |
|---|---|---|
| Nodes | 5,142 | 5,139 |
| Relationships | 20,312 | 20,375 |
| Node labels | 45 | 52 |
| Relationship types | 80 | 108 |

Most of the graph is the materialized supply network (3,521 materials and their bill of materials). The ontology layers (concepts, rules, policies, data products, process, tools, agents) are a few hundred nodes.

Note: earlier versions of the enablement deck said "about 10,000 nodes and 22,000 relationships"; the graph as built has about 5,100 nodes and 20,300 relationships.

## Nodes by label

| Label | Conversation | Execution |
|---|---|---|
| Material | 3521 | 3521 |
| Value | 567 | 567 |
| Supplier | 270 | 270 |
| Column | 255 | 255 |
| SqlStep | 60 | — |
| Table | 54 | 54 |
| Expression | 51 | 51 |
| Query | 50 | 50 |
| BusinessTerm | 37 | 37 |
| Concept | 28 | 34 |
| StandardTerm | 27 | 27 |
| Territory | 24 | 24 |
| Tool | — | 19 |
| RejectCode | 16 | 16 |
| State | 15 | 15 |
| DecisionTrace | 15 | — |
| BusinessTask | — | 14 |
| PackagedProduct | 12 | 12 |
| Metric | 11 | 11 |
| SoftwareApplication | — | 10 |
| MedicinalProduct | 10 | 10 |
| Role | 5 | 9 |
| DataProduct | 7 | 8 |
| BusinessRule | 5 | 8 |
| Standard | 7 | 7 |
| JoinPath | 7 | 7 |
| Team | 6 | 7 |
| Schema | 7 | 7 |
| Join | 7 | 7 |
| RejectGroup | 7 | 7 |
| Channel | 6 | 6 |
| Wholesaler | 6 | 6 |
| District | 6 | 6 |
| Policy | 5 | 5 |
| BusinessActivity | — | 5 |
| CoverageTier | 5 | 5 |
| SupplyContract | 5 | 5 |
| Category | 4 | 4 |
| Step | 4 | 4 |
| Plant | 4 | 4 |
| ExecutionTrace | — | 3 |
| DistributionCenter | 3 | 3 |
| Aspect | 2 | 2 |
| Agent | — | 2 |
| KnowledgeAsset | — | 2 |
| Database | 2 | 2 |
| TherapeuticMarket | 2 | 2 |
| Domain | 2 | 2 |
| Report | 2 | 2 |
| BusinessProcess | — | 1 |
| __neocarta_graph__ | 1 | 1 |
| ExternalFeed | — | 1 |
| Process | 1 | 1 |
| Glossary | 1 | 1 |

## Relationships by type

| Type | Conversation | Execution |
|---|---|---|
| COMPONENT_OF | 7043 | 7043 |
| SUPPLIES | 5265 | 5265 |
| INSTANCE_OF | 3912 | 3912 |
| MAKES | 1405 | 1405 |
| HAS_VALUE | 567 | 567 |
| USES_COLUMN | 320 | 320 |
| WAS_COMPONENT_OF | 281 | 281 |
| HAS_COLUMN | 255 | 255 |
| USED | 169 | 35 |
| USES_TABLE | 120 | 120 |
| MAPPED_TO | 101 | 101 |
| HAS_TABLE | 68 | 68 |
| RAN | 60 | — |
| ABOUT | 57 | 48 |
| HAS_EXPRESSION | 51 | 51 |
| TAGGED_WITH | 46 | 46 |
| REFERENCES | 38 | 38 |
| HAS_BUSINESS_TERM | 37 | 37 |
| APPLIES_TO | 23 | 35 |
| STEWARDS | 34 | 34 |
| INCLUDES | 33 | 33 |
| MAY_USE | — | 32 |
| REALIZES | 31 | 31 |
| ALIGNED_WITH | 29 | 29 |
| DEFINED_BY | 27 | 27 |
| STEP | 27 | 27 |
| IN_DISTRICT | 25 | 25 |
| COMPUTED_FROM | 22 | 22 |
| WRAPS | — | 22 |
| USES_TOOL | — | 20 |
| NEXT | 3 | 20 |
| FOLLOWED | — | 18 |
| STOCKS | 16 | 16 |
| IN_GROUP | 16 | 16 |
| SERVES_STATE | 15 | 15 |
| INVOLVES | 15 | 15 |
| HAS_TASKS | — | 14 |
| PERFORMS | — | 14 |
| USED_IN_JOIN | 14 | 14 |
| ACCESSED | — | 14 |
| PACKAGES | 13 | 13 |
| GOVERNS | — | 13 |
| IN_MARKET | 13 | 13 |
| READS_DATA | — | 12 |
| RATIFIED_BY | 11 | 11 |
| HAS_METRIC | 11 | 11 |
| MEASURES | 11 | 11 |
| OWNS_SYSTEM | — | 9 |
| MEMBER_OF | 5 | 9 |
| OWNS | 7 | 9 |
| SUPPORTS_TASK | — | 8 |
| OWNS_RULE | 5 | 8 |
| FROM_CONCEPT | 7 | 7 |
| HAS_SCHEMA | 7 | 7 |
| DEFINES_SCHEMA | — | 7 |
| HAS_TARGET_TABLE | 7 | 7 |
| HAS_SOURCE_TABLE | 7 | 7 |
| TO_CONCEPT | 7 | 7 |
| CREATES_DATA | — | 7 |
| SYSTEM_OF_RECORD | — | 6 |
| IS_PACKAGED_AS | 6 | 6 |
| USED_IN | 6 | 6 |
| SHIPS_TO | 6 | 6 |
| LAST_STEP | — | 5 |
| FIRST_STEP | — | 5 |
| OWNS_POLICY | 5 | 5 |
| HAS_ACTIVITIES | — | 5 |
| READS | 5 | 5 |
| FOR | 4 | 4 |
| EXPOSES | — | 4 |
| HAS_STEP | 4 | 4 |
| CHECKED | 4 | — |
| HAS_CATEGORY | 4 | 4 |
| GENERATED_BY | — | 3 |
| RESTRICTS | 3 | 3 |
| REGISTERS | — | 2 |
| PUBLISHES | 2 | 2 |
| SEEDS | — | 2 |
| HAS_ASPECT | 2 | 2 |
| COVERS | 2 | 2 |
| PERMITS | 2 | 2 |
| FEED_CONTENTS | — | 2 |
| TO | 2 | 2 |
| SUPERSEDES | — | 1 |
| IN_TERRITORY | 1 | 1 |
| IN_CHANNEL | 1 | 1 |
| MAY_RUN | — | 1 |
| DISRUPTION_HANDLED_BY | — | 1 |
| TARGETS | 1 | 1 |
| OF | 1 | 1 |
| MAY_HAVE | 1 | 1 |
| PERFORMS_PROCESS | — | 1 |
| BY | 1 | 1 |
| OFFERED_BY | 1 | 1 |
| HAS_FORMULARY | 1 | 1 |
| APPROVED_SUBSTITUTE | 1 | 1 |
| HANDOFF_TO | — | 1 |
| RECEIVES | — | 1 |
| FILLS | 1 | 1 |
| AFFILIATED_WITH | 1 | 1 |
| FROM | 1 | 1 |
| REUSES | — | 1 |
| ON | 1 | 1 |
| UNDER | 1 | 1 |
| VARIANT_OF | 1 | 1 |
| LINKS | 1 | 1 |
| PART_OF | 1 | 1 |
| WRITTEN_BY | 1 | 1 |
| ESCALATES_TO | — | 1 |
| COVERED_BY | 1 | 1 |

The model these were built from is in [model/](model/): `conversation/` as on main, `execution/` as on execution-pattern.
