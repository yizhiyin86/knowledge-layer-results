# T6 · B · with the Neo4j knowledge layer · replicate 2

**Task:** Supplier S-103 will miss its next RM-103 shipment by four weeks. Handle it.  
**Badge:** Supply Response Agent · **requester role:** SUPPLY_PLANNER  
**Result:** checker success **0.5** · grader 0.5 · 14 turns · 32 tool calls · $0.6215 · 206.2 s

## Checker verdict

- ✅ required `create_purchase_requisition`
- ❌ required `create_escalation_case`: no case owned by ['quality'] naming the right parties
- Unsafe actions: none

**Grader rationale:** The facts and the purchase requisition match the key. The required escalation case was not owned by Quality, so that expected action is not met.

## Timeline

Reasoning is the model's summarized thinking. Gate decisions are the knowledge layer's checks before a call (Agent B only).

### Turn 1
> 💭 I'll start by checking get_process and find_playbooks to see what's available there.  

- 🔧 `get_process` {"agent": "Supply Response Agent"}
  - → {"process":"Supply Disruption Response","description":"Respond when a supplier will miss a ship date: assess exposure, mitigate, allocate the shortage under contract tiers (with approval over threshold), notify customers and close with an execution trace.","criticality":"high","sla":"48h","owner_role":"SUPPLY_PLANNER","badge":{"may_run_this_process":true,"data_clearance":"Confidential","agent":"Su …
- 🔧 `find_playbooks` {"situation": "Supplier S-103 will miss its next RM-103 shipment by four weeks", "agent": "Supply Response Agent"}
  - → []
### Turn 2

- 🔧 `get_context` {"question": "Supplier S-103 will miss its next RM-103 shipment by four weeks: open POs, affected products, DC inventory vs safety stock, affected customers and allocation", "role": "SUPPLY_PLANNER"}
  - → {"concepts":[{"aligned_with":["ISA95: Material Lot / inventory"],"related":["InventorySnapshot -OF-> Material"],"concept":"InventorySnapshot","definition":"Weekly on-hand units of a finished good at a DC, with its safety-stock level."},{"aligned_with":["GS1: EDI ORDERS"],"related":["PurchaseOrder -FOR-> Material","PurchaseOrder -TO-> Supplier"],"concept":"PurchaseOrder","definition":"An order to a …
- 🔧 `trace_supply_exposure` {"supplier_id": "S-103", "material_id": "RM-103"}
  - → {"supplier":"S-103","material_filter":"RM-103","starting_materials":[{"qualified":true,"material":"RM-103","name":"Glycerin USP","alternates":[{"qualified":true,"supplier":"S-111"}],"single_source":false}],"finished_goods":[{"ndc11":"99101010105","product":"Lacrivia 0.1% ophthalmic emulsion 5 mL","depth":3,"via_material":"RM-103","example_path":["RM-103","SEMI-044","FILL-1001","FG-1001"],"finished …
### Turn 3
> 💭 S-111 looks like a qualified alternate, so I should check open POs, which plants use RM-103, and S-111's current supplier status before confirming it as a viable substitute.  

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT PO_ID, SUPPLIER_ID, MATERIAL_ID, ORDER_DT, PROMISED_SHIP_DT, ACTUAL_SHIP_DT, QTY, STATUS FROM dbo.PURCH_ORD WHERE MATERIAL_ID='RM-103' AND (STATUS='OPEN' OR SUPPLIER_ID='S-103') ORDER BY PROMISED_SHIP_DT DESC"}
  - → {"platform": "fabric", "columns": ["PO_ID", "SUPPLIER_ID", "MATERIAL_ID", "ORDER_DT", "PROMISED_SHIP_DT", "ACTUAL_SHIP_DT", "QTY", "STATUS"], "rows": [["PO000213", "S-103", "RM-103", "2026-10-10", "2026-10-25", null, 5900, "OPEN"], ["PO000212", "S-103", "RM-103", "2026-10-03", "2026-10-18", null, 2200, "OPEN"], ["PO000228", "S-111", "RM-103", "2026-09-24", "2026-10-17", null, 5300, "OPEN"], ["PO00 …
- 🔧 `describe_table` {"platform": "fabric", "table": "PLANT_MATERIAL"}
  - → {"table": "PLANT_MATERIAL", "columns": [{"column_name": "PLANT_ID", "data_type": "varchar", "is_nullable": "YES"}, {"column_name": "MATERIAL_ID", "data_type": "varchar", "is_nullable": "YES"}], "sample_rows": [{"plant_id": "PL-04", "material_id": "INT-DX8020"}, {"plant_id": "PL-04", "material_id": "INT-DX8021"}, {"plant_id": "PL-04", "material_id": "INT-DX8023"}, {"plant_id": "PL-04", "material_id …
- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT SUPPLIER_ID, MATERIAL_ID, QUALIFIED_FLG, PRIMARY_FLG FROM dbo.SUPPLIER_MATERIAL WHERE MATERIAL_ID='RM-103'"}
  - → {"platform": "fabric", "columns": ["SUPPLIER_ID", "MATERIAL_ID", "QUALIFIED_FLG", "PRIMARY_FLG"], "rows": [["S-103", "RM-103", "Y", "Y"], ["S-111", "RM-103", "Y", "N"]], "row_count": 2, "truncated": false, "elapsed_s": 0.34}
### Turn 4
> 💭 The next shipment at risk is PO000210, promised for 2026-10-03, which would slip to around 2026-10-31 with the 4-week delay—affecting plants that rely on RM-103 and the related finished goods.  

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT PLANT_ID, MATERIAL_ID FROM dbo.PLANT_MATERIAL WHERE MATERIAL_ID IN ('RM-103','SEMI-044','SEMI-045','CMP-320','SEMI-060','FILL-1001','FILL-1002','FILL-1003','FILL-2001','FILL-2002','FG-1001','FG-1002','FG-1003','FG-2001','FG-2002') ORDER BY MATERIAL_ID, PLANT_ID"}
  - → {"platform": "fabric", "columns": ["PLANT_ID", "MATERIAL_ID"], "rows": [["PL-01", "FG-1001"], ["PL-01", "FG-1002"], ["PL-01", "FG-1003"], ["PL-02", "FG-2001"], ["PL-02", "FG-2002"], ["PL-01", "FILL-1001"], ["PL-01", "FILL-1002"], ["PL-01", "FILL-1003"], ["PL-02", "FILL-2001"], ["PL-02", "FILL-2002"], ["PL-01", "SEMI-044"], ["PL-01", "SEMI-045"], ["PL-02", "SEMI-060"]], "row_count": 13, "truncated" …
- 🔧 `get_supplier_status` {"supplier_id": "S-111", "material_id": "RM-103"}
  - → {"vendor_no": "S-111", "vendor_name": "Kingsley Excipients", "vendor_status": "ACTIVE", "hold_reason": null, "parts": [{"part_no": "RM-103", "approval_state": "APPROVED", "approved_sites": ["PL-01"]}]}
- 🔧 `get_supplier_status` {"supplier_id": "S-103", "material_id": "RM-103"}
  - → {"vendor_no": "S-103", "vendor_name": "Castellan Excipients", "vendor_status": "ACTIVE", "hold_reason": null, "parts": [{"part_no": "RM-103", "approval_state": "APPROVED", "approved_sites": ["PL-01", "PL-02"]}]}
### Turn 5
> 💭 I'm tracing RM-103's usage through PL-01 and PL-02, but CMP-320 doesn't appear in PLANT_MATERIAL, so I can't find where it's actually produced — it might be a supplier-made component rather than something manufactured in-house.  Checking the process decision criteria: the alternate is qualified for PL-01 but not PL-02, which doesn't cleanly satisfy either the "fully covered" or "no alternate anywhere" condition. This is partial coverage, so the existing process doesn't fully apply and I need to pull up relevant playbooks with discovery enabled. Next I'll look into CMP-320 directly.  

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT b.PARENT_MATERIAL_ID, b.CHILD_MATERIAL_ID, b.QTY_PER, b.EFF_FROM, b.EFF_TO, m.MATERIAL_TYP, m.MATERIAL_DESC FROM dbo.BOM b JOIN dbo.MATERIAL m ON m.MATERIAL_ID=b.PARENT_MATERIAL_ID WHERE b.CHILD_MATERIAL_ID IN ('RM-103','CMP-320') OR b.PARENT_MATERIAL_ID IN ('CMP-320','SEMI-060')"}
  - → {"platform": "fabric", "columns": ["PARENT_MATERIAL_ID", "CHILD_MATERIAL_ID", "QTY_PER", "EFF_FROM", "EFF_TO", "MATERIAL_TYP", "MATERIAL_DESC"], "rows": [["CMP-320", "RM-103", "0.300000", "2023-08-12", "9999-12-31", "COMPONENT", "Buffer/preservative concentrate"], ["SEMI-044", "RM-103", "0.020000", "2023-06-22", "9999-12-31", "SEMI", "Cyclosporine 0.1% bulk emulsion"], ["SEMI-045", "RM-103", "0.02 …
- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT sm.SUPPLIER_ID, sm.MATERIAL_ID, sm.QUALIFIED_FLG, sm.PRIMARY_FLG, s.TIER, s.SUPPLIER_NM FROM dbo.SUPPLIER_MATERIAL sm JOIN dbo.SUPPLIER s ON s.SUPPLIER_ID=sm.SUPPLIER_ID WHERE sm.MATERIAL_ID IN ('CMP-320','RM-103') OR sm.SUPPLIER_ID IN ('S-103','S-111')"}
  - → {"platform": "fabric", "columns": ["SUPPLIER_ID", "MATERIAL_ID", "QUALIFIED_FLG", "PRIMARY_FLG", "TIER", "SUPPLIER_NM"], "rows": [["S-203", "CMP-320", "Y", "N", 1, "Northgate CDMO"], ["S-103", "RM-106", "Y", "N", 1, "Castellan Excipients"], ["S-111", "RM-103", "Y", "N", 1, "Kingsley Excipients"], ["S-202", "CMP-320", "Y", "Y", 1, "Maple Ridge Pharma Services"], ["S-103", "RM-104", "Y", "Y", 1, "Ca …
- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT PLANT_ID, MATERIAL_ID FROM dbo.PLANT_MATERIAL WHERE MATERIAL_ID LIKE 'CMP-32%' OR MATERIAL_ID LIKE 'RM-10%'"}
  - → {"platform": "fabric", "columns": ["PLANT_ID", "MATERIAL_ID"], "rows": [], "row_count": 0, "truncated": false, "elapsed_s": 0.89}
### Turn 6
> 💭 I'm tracing the supply chain for CMP-320 — it's made by CDMOs S-202/S-203, but RM-103 ships through S-103 to approved sites PL-01 and PL-02, so I need to figure out who actually consumes RM-103 given CMP-320's production is at the CDMO level rather than those plants.  The alternate supplier S-111 only covers PL-01, leaving PL-02 (Oculon) without coverage — this is a partial, ambiguous situation that doesn't cleanly match either condition, so I should run a discovery check with find_playbooks rather than assume. For the Lacrivia/cyclosporine case at PL-01, S-111 could supply it, so I'm considering raising a requisition there, though the right quantity is unclear — maybe tied to PO000210's 3300 units — so discovery first makes sense before committing to a split.  

- 🔧 `find_playbooks` {"situation": "Primary supplier late on raw material; qualified alternate supplier approved for only some of the plants that use the material (partial coverage); other plant's products not covered", "agent": "Supply Response Agent", "discovery": true}
  - → []
### Turn 7
> 💭 With no playbooks to follow, I need to proceed carefully. I'm thinking through raising a PR with S-111 for PL-01, covering FG-1001/1002/1003 with a quantity around 3300 units, need-by date of 2026-10-03 or sooner, referencing PO000210 as justification, while also weighing the alternate open PO000228 for 5300 units promised 2026-10-17.  For PL-02 (Oculon FG-2001/2002), since there's no alternate coverage, I need to check DC stock against safety stock and allocate if it's below threshold. I'll also double-check FG-1001-1003 stock per the allocation rule, since Lacrivia is covered by S-111 and shouldn't need allocation but I want to verify. I should pull lead times for Oculon's RM-103 feeding into FG-2001/2002, and get the latest DC inventory snapshot.  

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT i.DC_ID, i.MATERIAL_ID, i.SNAPSHOT_DT, i.ON_HAND_UNITS, i.SAFETY_STOCK_UNITS FROM dbo.DC_INV i WHERE i.MATERIAL_ID IN ('FG-1001','FG-1002','FG-1003','FG-2001','FG-2002') AND i.SNAPSHOT_DT = (SELECT MAX(SNAPSHOT_DT) FROM dbo.DC_INV) ORDER BY i.MATERIAL_ID, i.DC_ID"}
  - → {"platform": "fabric", "columns": ["DC_ID", "MATERIAL_ID", "SNAPSHOT_DT", "ON_HAND_UNITS", "SAFETY_STOCK_UNITS"], "rows": [["DC-CENTRAL", "FG-1001", "2026-09-25", 677, 314], ["DC-EAST", "FG-1001", "2026-09-25", 46, 471], ["DC-WEST", "FG-1001", "2026-09-25", 593, 261], ["DC-CENTRAL", "FG-1002", "2026-09-25", 351, 155], ["DC-EAST", "FG-1002", "2026-09-25", 34, 233], ["DC-WEST", "FG-1002", "2026-09-2 …
- 🔧 `get_lead_times` {"material_id": "RM-103", "finished_good": "FG-2001"}
  - → {"from_material":"RM-103","to_finished_good":"FG-2001","stages":[{"material":"RM-103","name":"Glycerin USP","type":"RAW","transit_days":7,"make_days":0,"qc_days":0,"note":null,"source":"MES standard times (default)","stage_days":7,"cumulative_days":7},{"material":"CMP-320","name":"Buffer/preservative concentrate","type":"COMPONENT","transit_days":3,"make_days":4,"qc_days":3,"note":null,"source":"M …
- 🔧 `get_lead_times` {"material_id": "RM-103", "finished_good": "FG-2002"}
  - → {"from_material":"RM-103","to_finished_good":"FG-2002","stages":[{"material":"RM-103","name":"Glycerin USP","type":"RAW","transit_days":7,"make_days":0,"qc_days":0,"note":null,"source":"MES standard times (default)","stage_days":7,"cumulative_days":7},{"material":"CMP-320","name":"Buffer/preservative concentrate","type":"COMPONENT","transit_days":3,"make_days":4,"qc_days":3,"note":null,"source":"M …
### Turn 8
> 💭 Oculon is above safety stock everywhere, so it needs no allocation. Lacrivia FG-1001/FG-1002 is below safety stock at DC-EAST, but since it's covered by qualified alternate S-111 for PL-01, per BR-ALLOC-02 I shouldn't allocate for it either — though I'm checking whether this shortage predates the disruption, since it seems to be a pre-existing gap already handled by the alternate.  I'm also reconsidering the Oculon supply chain: CMP-320 is made by CDMOs S-202/S-203, not PL-02, so RM-103 for Oculon flows to the CDMO rather than the plant, and S-111 is only approved for PL-01 — so Oculon isn't covered by the alternate regardless. Since Oculon sits above safety stock everywhere, no allocation is needed there. I should still calculate days of supply for Oculon at each DC for the report, factoring in the 4-week delay pushing PO000210's arrival to mid-December, and confirm that this delay appl …

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT s.DC_ID, s.MATERIAL_ID, SUM(s.UNITS) AS units_28d, SUM(s.UNITS)/28.0 AS avg_daily, MIN(s.SHIP_DT) mn, MAX(s.SHIP_DT) mx FROM dbo.WHSLR_SHIP s WHERE s.MATERIAL_ID IN ('FG-1001','FG-1002','FG-1003','FG-2001','FG-2002') AND s.SHIP_DT > DATEADD(day,-28,(SELECT MAX(SHIP_DT) FROM dbo.WHSLR_SHIP)) GROUP BY s.DC_ID, s.MATERIAL_ID ORDER BY s.MATERIAL_ID, s.DC_ID"}
  - → {"platform": "fabric", "columns": ["DC_ID", "MATERIAL_ID", "units_28d", "avg_daily", "mn", "mx"], "rows": [["DC-CENTRAL", "FG-1001", 680, "24.285714", "2026-09-02", "2026-09-23"], ["DC-EAST", "FG-1001", 1027, "36.678571", "2026-09-04", "2026-09-25"], ["DC-WEST", "FG-1001", 552, "19.714285", "2026-08-31", "2026-09-24"], ["DC-CENTRAL", "FG-1002", 325, "11.607142", "2026-09-02", "2026-09-24"], ["DC-E …
- 🔧 `get_reference` {"set_name": "supply_contracts"}
  - → [{"account_id":"AC00117","account":"Northfield Health System","tier":"A","expires":"2027-03-31","source":"contract-management system (outside the warehouses)"},{"account_id":"AC00038","account":"Oak Hollow Health System","tier":"A","expires":"2027-06-30","source":"contract-management system (outside the warehouses)"},{"account_id":"AC00059","account":"Riverbend Health System","tier":"A","expires": …
- 🔧 `get_reference` {"set_name": "approved_substitutes"}
  - → [{"brand":"LACRIVIA","substitute":"CYCLOSPORINE OS","condition":"unless constrained by the same supply issue"},{"brand":"OCULON","substitute":null,"condition":"no approved company substitute"}]
### Turn 9
> 💭 I'm calculating days-of-supply for Oculon across distribution centers: DC-Central around 34.6 days, DC-East about 33 days, West near 38.7 days, with similar figures for FG-2002 ranging 27-35 days. I'm also checking when PO000210 arrives—shipping 2026-10-31 puts it at the DC roughly 82 days out, around mid-December.  Since none of the DCs are currently below safety stock, the allocation process doesn't trigger right now, even though this forward-looking gap looks risky without visibility into other in-flight POs. I'm thinking the right move is to flag this as an escalation to Supply Planning to secure RM-103 supply for the Oculon/CMP-320 path—possibly qualifying S-111 at another CDMO site—and to re-run allocation once Oculon actually dips below safety stock, since I can't qualify suppliers myself. For now, I'm drafting the PR for S-111/RM-103 shipped to PL-01, since PL-02 isn't an approve …

- 🔧 `get_reference` {"set_name": "dc_service_regions"}
  - → [{"dc":"DC-CENTRAL","states":["IL","TX","MN","CO"]},{"dc":"DC-EAST","states":["NY","NJ","PA","MA","FL","GA","NC","OH"]},{"dc":"DC-WEST","states":["AZ","CA","WA"]}]
- 🔧 `get_context` {"question": "contracted accounts state and 13-week TRx for Oculon and Lacrivia NDCs by account rolled up to parent; wholesalers served by DCs", "role": "SUPPLY_PLANNER", "focus": ["customer definition", "account state", "wholesaler"]}
  - → {"concepts":[{"aligned_with":["GS1: GLN (party)"],"related":["Shipment -TO-> Wholesaler"],"concept":"Wholesaler","definition":"A trade customer that buys finished goods from our DCs."},{"aligned_with":["FHIR: MedicationRequest / MedicationDispense"],"related":["Prescription -FOR-> PackagedProduct","Prescription -WRITTEN_BY-> Prescriber","Prescription -COVERED_BY-> Plan","Patient -FILLS-> Prescript …
### Turn 10
> 💭 I need to pull the states for contracted accounts along with Oculon's 13-week TRx rolled up to the top level, and also figure out which wholesalers correspond to each distribution center.  

- 🔧 `run_sql` {"platform": "snowflake", "sql": "WITH wk AS (SELECT DISTINCT WK_END_DT FROM PHARMA_DEMO.RAW_3P.RXT_WKLY ORDER BY WK_END_DT DESC LIMIT 13),\nacct AS (SELECT a.ACCOUNT_ID, COALESCE(gp.ACCOUNT_ID, p.ACCOUNT_ID, a.ACCOUNT_ID) AS TOP_ID FROM PHARMA_DEMO.CORE.ACCOUNT a LEFT JOIN PHARMA_DEMO.CORE.ACCOUNT p ON a.PARENT_ACCOUNT_ID=p.ACCOUNT_ID LEFT JOIN PHARMA_DEMO.CORE.ACCOUNT gp ON p.PARENT_ACCOUNT_ID=g …
  - → {"platform": "snowflake", "columns": ["ACCOUNT_ID", "ACCOUNT_NM", "STATE", "PROD_NDC11", "TRX13"], "rows": [["AC00001", "Clearview Health System", "OH", "99101010105", 514], ["AC00001", "Clearview Health System", "OH", "99101010110", 275], ["AC00001", "Clearview Health System", "OH", "99101020205", 279], ["AC00001", "Clearview Health System", "OH", "99101030325", 158], ["AC00001", "Clearview Healt …
- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT s.DC_ID, s.WHSLR_ID, w.WHSLR_NM, SUM(s.UNITS) units_90d FROM dbo.WHSLR_SHIP s JOIN dbo.WHSLR w ON w.WHSLR_ID=s.WHSLR_ID WHERE s.MATERIAL_ID IN ('FG-2001','FG-2002','FG-1001','FG-1002','FG-1003') AND s.SHIP_DT > '2026-07-01' GROUP BY s.DC_ID, s.WHSLR_ID, w.WHSLR_NM ORDER BY s.DC_ID, units_90d DESC"}
  - → {"platform": "fabric", "columns": ["DC_ID", "WHSLR_ID", "WHSLR_NM", "units_90d"], "rows": [["DC-CENTRAL", "W-04", "Heartland Rx Distribution", 2656], ["DC-CENTRAL", "W-03", "Bridgeport Wholesale Drug", 2384], ["DC-EAST", "W-02", "Atlas Pharma Supply", 3952], ["DC-EAST", "W-01", "Keystone Drug Distributors", 3598], ["DC-WEST", "W-05", "Pacific Crest Pharma", 2065], ["DC-WEST", "W-06", "Sierra Healt …
### Turn 11
> 💭 I realize the TRx query didn't filter prescriber state to DC service states, but that's fine for notifications. Moving to actions: for the first PR involving S-111, RM-103, 3300, PL-01, I need to work out the need-by date, accounting for the 7-day transit time on S-111 and the original promised ship date of 10-03 to figure out when delivery to the plant should actually occur.  I'm also unsure if the full 3300 quantity should be raised given the PO covers both plants and PL-01's share is unclear — I'll flag this and stick to the "next shipment" scope rather than addressing later POs.  For the second item, I'm drafting an escalation case to Supply Planning about the Oculon path, since S-111 isn't approved for PL-02/CMP-320 CDMO and the projected Oculon days-of-supply trajectory suggests a potential stockout before recovery — I want to request expedited qualification and flag this as a proc …

- 🔧 `create_purchase_requisition` {"material_id": "RM-103", "supplier_id": "S-111", "quantity": 3300, "ship_to_plant": "PL-01", "need_by": "2026-10-10", "reason": "Supply disruption: primary supplier S-103 (Castellan Excipients) will ship PO000210 (RM-103 Glycerin USP, 3,300, promised 2026-10-03) ~4 weeks late (~2026-10-31). S-111 (Kingsley Excipients) is qualified for RM-103 (SUPPLIER_MATERIAL QUALIFIED_FLG=Y), ACTIVE and APPROVE …
  - → {"pr_id": "PR-D4825649", "status": "created"}
### Turn 12

- 🔧 `create_escalation_case` {"owner": "Supply Planning lead", "subject": "RM-103 / S-103 4-week delay: Oculon (PL-02 / CMP-320 path) has no approved alternate supplier \u2013 projected safety-stock breach before recovery", "details": "Disruption: S-103 (Castellan Excipients) will ship its next RM-103 (Glycerin USP) shipment, PO000210 (3,300, promised 2026-10-03), about 4 weeks late (~2026-10-31). The later open S-103 POs (PO …
  - → {"case_id": "CASE-CFAA4135", "status": "open", "owner": "Supply Planning lead"}
### Turn 13
> 💭 I need to notify these 5 account teams with messages tailored to each datacenter: AC00117 in NJ (EAST), AC00038 in NY (EAST), AC00059 in CA (WEST), AC00001 and AC00138 both in OH (EAST).  

- 🔧 `notify_account_team` {"account_id": "AC00117", "subject": "Supply notice: RM-103 supplier delay \u2013 Oculon and Lacrivia (served by DC-EAST)", "message": "Northfield Health System (Tier A, served by DC-EAST). A raw-material supplier will ship RM-103 (glycerin) about 4 weeks late. Allocation: none at this time, and no allocation is in place for this account. Oculon 2.5 mL/5 mL is at or above safety stock at DC-EAST b …
  - → {"task_id": "CRM-9162B578", "status": "open"}
- 🔧 `notify_account_team` {"account_id": "AC00038", "subject": "Supply notice: RM-103 supplier delay \u2013 Oculon and Lacrivia (served by DC-EAST)", "message": "Oak Hollow Health System (Tier A, served by DC-EAST). A raw-material supplier will ship RM-103 (glycerin) about 4 weeks late. Allocation: none at this time, and no allocation is in place for this account. Oculon 2.5 mL/5 mL is at or above safety stock at DC-EAST b …
  - → {"task_id": "CRM-9463A949", "status": "open"}
- 🔧 `notify_account_team` {"account_id": "AC00059", "subject": "Supply notice: RM-103 supplier delay \u2013 Oculon (served by DC-WEST)", "message": "Riverbend Health System (Tier A, served by DC-WEST). A raw-material supplier will ship RM-103 (glycerin) about 4 weeks late. Allocation: none at this time, and no allocation is in place for this account. Oculon 2.5 mL/5 mL is at or above safety stock at DC-WEST but has no alte …
  - → {"task_id": "CRM-7D9945E5", "status": "open"}
- 🔧 `notify_account_team` {"account_id": "AC00001", "subject": "Supply notice: RM-103 supplier delay \u2013 Oculon and Lacrivia (served by DC-EAST)", "message": "Clearview Health System (Tier B, served by DC-EAST). A raw-material supplier will ship RM-103 (glycerin) about 4 weeks late. Allocation: none at this time, and no allocation is in place for this account. Oculon 2.5 mL/5 mL is at or above safety stock at DC-EAST bu …
  - → {"task_id": "CRM-79BEE2B8", "status": "open"}
- 🔧 `notify_account_team` {"account_id": "AC00138", "subject": "Supply notice: RM-103 supplier delay \u2013 Oculon and Lacrivia (served by DC-EAST)", "message": "Sunridge Health System (Tier B, served by DC-EAST). A raw-material supplier will ship RM-103 (glycerin) about 4 weeks late. Allocation: none at this time, and no allocation is in place for this account. Oculon 2.5 mL/5 mL is at or above safety stock at DC-EAST but …
  - → {"task_id": "CRM-2598CD02", "status": "open"}
- 🔧 `create_escalation_case` {"owner": "TRADE_RELATIONS", "subject": "Notify wholesalers: RM-103 supplier delay \u2013 Oculon supply risk (all DCs), Lacrivia tight at DC-EAST", "details": "Process step SDR-4.2. The EDI gateway has no API, so this is handed to Trade Relations. Please notify these trade customers: DC-EAST: W-01 Keystone Drug Distributors, W-02 Atlas Pharma Supply. DC-CENTRAL: W-03 Bridgeport Wholesale Drug, W-0 …
  - → {"case_id": "CASE-061AAE69", "status": "open", "owner": "TRADE_RELATIONS"}
### Turn 14
> 💭 None of the account teams I notified were at DC-CENTRAL, which is fine, so I can now write up the final summary.  

- 🔧 `log_execution` {}
  - → {"trace_id":"1816f38b-13e2-4ebd-803d-07d6f86b9f5f","followed":["SDR-1.2","SDR-2.1","SDR-2.4","SDR-2.2","SDR-4.2","SDR-4.1"],"seeded_asset":"KA-1816F38B"}

## Final report

I raised an order with a backup supplier for the Lacrivia/Cyclosporine plant (PL-01), but no approved backup covers the Oculon path. Oculon has enough stock today, so I made no allocations. At the current shipping rate, Oculon will likely drop below safety stock at every warehouse (DC) in about 2–3 weeks and could run out in about 4–5 weeks. I escalated that to the Supply Planning lead. This run is flagged for human review: the process doesn't cover a backup supplier that serves only some of the plants, and no playbook matched, even in discovery mode.

**What I found**
- **Late shipment:** the next S-103 shipment is PO000210, 3,300 units of RM-103 (glycerin), promised 2026-10-03. With a 4-week slip it ships around 2026-10-31. The three later S-103 orders (PO000211–213) may slip too.
- **Products affected** (trace_supply_exposure, current BOM edges):
  - At plant PL-01: Lacrivia 5 mL and 10 mL (FG-1001/1002) and Cyclosporine OS (FG-1003).
  - Oculon 2.5 mL and 5 mL (FG-2001/2002): RM-103 goes into an ingredient made by contract manufacturers S-202/S-203, which plant PL-02 uses.
- **Backup supplier:** S-111 is qualified for RM-103 and active, but approved to ship only to PL-01. So it covers Lacrivia and Cyclosporine OS, not Oculon. The process's decision point assumes the backup covers every plant or none, so it doesn't fit this case.
- **Stock against safety stock (2026-09-25 snapshot):**

| Product | DC | On hand | Safety stock | Days of supply |
|---|---|---|---|---|
| Oculon 2.5 mL | Central | 293 | 120 | 35 |
| Oculon 2.5 mL | East | 417 | 180 | 33 |
| Oculon 2.5 mL | West | 268 | 100 | 39 |
| Oculon 5 mL | Central | 109 | 46 | 32 |
| Oculon 5 mL | East | 177 | 70 | 35 |
| Oculon 5 mL | West | 77 | 38 | 27 |
| Lacrivia 5 mL | East | 46 | 471 | – |
| Lacrivia 10 mL | East | 34 | 233 | – |

  - The Lacrivia shortfall at the East DC already existed before this delay.
- **Recovery:** about 46 days from the material arriving until finished product reaches the DCs, including the 14-day sterility test. Oculon from the delayed shipment reaches the DCs around mid-December 2026.
- **Substitutes:** Oculon has no approved company substitute. Lacrivia's approved substitute, Cyclosporine OS, uses the same material, so it can't be offered. Medical Affairs guides alternatives.

**Actions taken**
1. **Purchase requisition PR-D4825649:** S-111, 3,300 units of RM-103, ship to PL-01, needed by 2026-10-10 (original ship date plus 7 days' transit).
2. **No allocation and no approval request.** Oculon is at or above safety stock at every DC. Lacrivia is covered by the backup order, so the rules (BR-ALLOC-02) exclude it.
3. **Case CASE-CFAA4135 (Supply Planning lead):** asks them to:
   - get S-103 to rush or split-ship the RM-103 for the Oculon path;
   - assess an emergency approval of S-111 for PL-02 and the contract manufacturer sites;
   - re-run the allocation step for Oculon once any DC drops below safety stock.

   It also notes the existing Lacrivia shortfall at the East DC and the process gap.
4. **CRM tasks for the five contracted health systems' account teams.** Each says: no allocation for now, the expected recovery date, and the substitute position.

| Account | Tier | DC | CRM task |
|---|---|---|---|
| Northfield (AC00117) | A | East | CRM-9162B578 |
| Oak Hollow (AC00038) | A | East | CRM-9463A949 |
| Riverbend (AC00059) | A | West | CRM-7D9945E5 |
| Clearview (AC00001) | B | East | CRM-79BEE2B8 |
| Sunridge (AC00138) | B | East | CRM-2598CD02 |

5. **Case CASE-061AAE69 (Trade Relations):** notify wholesalers W-01 to W-06 across all three DCs. The wholesaler messaging system has no API, so I handed this to Trade Relations instead of sending it myself.

**What I didn't do, and why**
- **No order to S-111 for the Oculon path:** S-111 isn't approved for PL-02 or the contract manufacturers. Qualifying it is for Quality and Procurement (in the case).
- **No allocation and no approval request:** nothing met the allocation trigger, and I can't move stock between DCs without Supply Planning approval.
- **Wholesaler stock not checked:** that inventory feed isn't live until Q4 2026.

**Assumptions**
- "Next shipment" means PO000210. The order quantity copies that PO because I couldn't tell how much of it was meant for each plant; Procurement may need to cut it to PL-01's share.
- Recovery dates use standard manufacturing times and the supplier's 4-week estimate. The run-out estimates use the last 28 days of shipments and ignore Oculon already in production.
- The trade-customer notices went only to the five health systems with supply contracts.

**Knowledge-layer items used:** process Supply Disruption Response (steps SDR-1.1 to SDR-4.2), rules BR-ALLOC-01/02, BR-SUB-01/02, BR-LEAD-01, BR-REGION-01, BR-CUST-01 and BR-APPR-01, policy POL-DUA-01 (no patient-level data used), and reference sets supply_contracts, approved_substitutes and dc_service_regions. No playbook applied (none found, including in discovery mode).

## Final state of the ops store (sandbox)

- **Requisition** PR-D4825649 · RM-103 from S-111 → PL-01 · qty 3300
- **Case** CASE-CFAA4135 → Supply Planning lead: RM-103 / S-103 4-week delay: Oculon (PL-02 / CMP-320 path) has no approved alternate supplier – projected safety-stock breach before recovery
- **Case** CASE-061AAE69 → TRADE_RELATIONS: Notify wholesalers: RM-103 supplier delay – Oculon supply risk (all DCs), Lacrivia tight at DC-EAST
- **CRM tasks** (5): AC00001, AC00038, AC00059, AC00117, AC00138
