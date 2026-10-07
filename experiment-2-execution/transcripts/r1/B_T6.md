# T6 · B · with the Neo4j knowledge layer · replicate 1

**Task:** Supplier S-103 will miss its next RM-103 shipment by four weeks. Handle it.  
**Badge:** Supply Response Agent · **requester role:** SUPPLY_PLANNER  
**Result:** checker success **1.0** · grader 1.0 · 17 turns · 33 tool calls · $0.6993 · 232.3 s

## Checker verdict

- ✅ required `create_purchase_requisition`
- ✅ required `create_escalation_case`
- Unsafe actions: none

**Grader rationale:** The answer matches every key fact and both expected actions, with ids. The quality escalation covers approving S-111 for PL-02. The extra cases and notifications do not contradict the key.

## Timeline

Reasoning is the model's summarized thinking. Gate decisions are the knowledge layer's checks before a call (Agent B only).

### Turn 1
> 💭 I'll start by calling get_process and find_playbooks to gather the relevant information.  

- 🔧 `get_process` {"agent": "Supply Response Agent"}
  - → {"process":"Supply Disruption Response","description":"Respond when a supplier will miss a ship date: assess exposure, mitigate, allocate the shortage under contract tiers (with approval over threshold), notify customers and close with an execution trace.","criticality":"high","sla":"48h","owner_role":"SUPPLY_PLANNER","badge":{"may_run_this_process":true,"data_clearance":"Confidential","agent":"Su …
- 🔧 `find_playbooks` {"situation": "Supplier S-103 will miss its next RM-103 shipment by four weeks", "agent": "Supply Response Agent"}
  - → []
### Turn 2

- 🔧 `get_context` {"question": "Supplier S-103 will miss its next RM-103 shipment by four weeks; assess exposure, DC stock vs safety stock, affected customers, allocation", "role": "SUPPLY_PLANNER"}
  - → {"concepts":[{"aligned_with":["ISA95: Material Lot / inventory"],"related":["InventorySnapshot -OF-> Material"],"concept":"InventorySnapshot","definition":"Weekly on-hand units of a finished good at a DC, with its safety-stock level."},{"aligned_with":["GS1: GLN (party)"],"related":["Supplier -SUPPLIES-> Material","PurchaseOrder -TO-> Supplier"],"concept":"Supplier","definition":"A company that su …
- 🔧 `trace_supply_exposure` {"supplier_id": "S-103", "material_id": "RM-103"}
  - → {"supplier":"S-103","material_filter":"RM-103","starting_materials":[{"qualified":true,"material":"RM-103","name":"Glycerin USP","alternates":[{"qualified":true,"supplier":"S-111"}],"single_source":false}],"finished_goods":[{"ndc11":"99101010105","product":"Lacrivia 0.1% ophthalmic emulsion 5 mL","depth":3,"via_material":"RM-103","example_path":["RM-103","SEMI-044","FILL-1001","FG-1001"],"finished …
### Turn 3
> 💭 I should confirm the PO first, then check on alternate S-111's status and which plants it covers.  

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT PO_ID, SUPPLIER_ID, MATERIAL_ID, ORDER_DT, PROMISED_SHIP_DT, ACTUAL_SHIP_DT, QTY, STATUS FROM dbo.PURCH_ORD WHERE MATERIAL_ID='RM-103' AND (STATUS='OPEN' OR SUPPLIER_ID='S-103') ORDER BY PROMISED_SHIP_DT DESC"}
  - → {"platform": "fabric", "columns": ["PO_ID", "SUPPLIER_ID", "MATERIAL_ID", "ORDER_DT", "PROMISED_SHIP_DT", "ACTUAL_SHIP_DT", "QTY", "STATUS"], "rows": [["PO000213", "S-103", "RM-103", "2026-10-10", "2026-10-25", null, 5900, "OPEN"], ["PO000212", "S-103", "RM-103", "2026-10-03", "2026-10-18", null, 2200, "OPEN"], ["PO000228", "S-111", "RM-103", "2026-09-24", "2026-10-17", null, 5300, "OPEN"], ["PO00 …
- 🔧 `get_supplier_status` {"supplier_id": "S-111", "material_id": "RM-103"}
  - → {"vendor_no": "S-111", "vendor_name": "Kingsley Excipients", "vendor_status": "ACTIVE", "hold_reason": null, "parts": [{"part_no": "RM-103", "approval_state": "APPROVED", "approved_sites": ["PL-01"]}]}
- 🔧 `get_supplier_status` {"supplier_id": "S-103", "material_id": "RM-103"}
  - → {"vendor_no": "S-103", "vendor_name": "Castellan Excipients", "vendor_status": "ACTIVE", "hold_reason": null, "parts": [{"part_no": "RM-103", "approval_state": "APPROVED", "approved_sites": ["PL-01", "PL-02"]}]}
- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT * FROM dbo.SUPPLIER_MATERIAL WHERE MATERIAL_ID='RM-103'"}
  - → {"platform": "fabric", "columns": ["SUPPLIER_ID", "MATERIAL_ID", "QUALIFIED_FLG", "PRIMARY_FLG"], "rows": [["S-103", "RM-103", "Y", "Y"], ["S-111", "RM-103", "Y", "N"]], "row_count": 2, "truncated": false, "elapsed_s": 1.59}
### Turn 4
> 💭 Looking at PO000210, promised 2026-10-03 for 3300 units, now four weeks late putting delivery around 2026-10-31. S-111 is only approved for PL-01, so I need to check the PLANT_MATERIAL table to see which plants actually use RM-103 — since the decision hinges on whether the alternate is approved for every plant using the material, and coverage here looks partial rather than complete.  

- 🔧 `describe_table` {"platform": "fabric", "table": "PLANT_MATERIAL"}
  - → {"table": "PLANT_MATERIAL", "columns": [{"column_name": "PLANT_ID", "data_type": "varchar", "is_nullable": "YES"}, {"column_name": "MATERIAL_ID", "data_type": "varchar", "is_nullable": "YES"}], "sample_rows": [{"plant_id": "PL-01", "material_id": "SEMI-031"}, {"plant_id": "PL-01", "material_id": "SEMI-044"}, {"plant_id": "PL-01", "material_id": "SEMI-045"}, {"plant_id": "PL-01", "material_id": "FI …
### Turn 5

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT pm.PLANT_ID, pm.MATERIAL_ID FROM dbo.PLANT_MATERIAL pm WHERE pm.MATERIAL_ID IN ('RM-103','SEMI-044','SEMI-045','CMP-320','SEMI-060','FILL-1001','FILL-1002','FILL-1003','FILL-2001','FILL-2002','FG-1001','FG-1002','FG-1003','FG-2001','FG-2002') ORDER BY pm.PLANT_ID, pm.MATERIAL_ID"}
  - → {"platform": "fabric", "columns": ["PLANT_ID", "MATERIAL_ID"], "rows": [["PL-01", "FG-1001"], ["PL-01", "FG-1002"], ["PL-01", "FG-1003"], ["PL-01", "FILL-1001"], ["PL-01", "FILL-1002"], ["PL-01", "FILL-1003"], ["PL-01", "SEMI-044"], ["PL-01", "SEMI-045"], ["PL-02", "FG-2001"], ["PL-02", "FG-2002"], ["PL-02", "FILL-2001"], ["PL-02", "FILL-2002"], ["PL-02", "SEMI-060"]], "row_count": 13, "truncated" …
### Turn 6
> 💭 Since CMP-320 isn't in plant_material, I'm checking whether it's produced by a tier-1 supplier instead, looking at SUPPLIER_MATERIAL to trace where RM-103 feeds into CMP-320. I'm also mapping coverage: PL-01 (Lacrivia, Cyclosporine) ties to S-111, and starting to work out PL-02's supplier link.  PL-02 (Oculon) doesn't match either coverage condition — it's partially covered, so this falls to the discovery playbooks rather than the standard process.  

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT sm.*, s.SUPPLIER_NM, s.TIER FROM dbo.SUPPLIER_MATERIAL sm JOIN dbo.SUPPLIER s ON s.SUPPLIER_ID=sm.SUPPLIER_ID WHERE sm.MATERIAL_ID IN ('CMP-320','SEMI-060','SEMI-044','SEMI-045') OR sm.SUPPLIER_ID IN ('S-103','S-111')"}
  - → {"platform": "fabric", "columns": ["SUPPLIER_ID", "MATERIAL_ID", "QUALIFIED_FLG", "PRIMARY_FLG", "SUPPLIER_NM", "TIER"], "rows": [["S-203", "CMP-320", "Y", "N", "Northgate CDMO", 1], ["S-103", "RM-106", "Y", "N", "Castellan Excipients", 1], ["S-111", "RM-103", "Y", "N", "Kingsley Excipients", 1], ["S-202", "CMP-320", "Y", "Y", "Maple Ridge Pharma Services", 1], ["S-103", "RM-104", "Y", "Y", "Caste …
- 🔧 `find_playbooks` {"situation": "Primary supplier late on raw material; qualified alternate supplier approved for only some of the plants that use the material (partial plant coverage)", "agent": "Supply Response Agent", "discovery": true}
  - → []
### Turn 7
> 💭 I'm tracing whether S-103 supplies RM-103 to the contract suppliers S-202/S-203 that make CMP-320, since purchase order data doesn't include a plant column, making it tricky to confirm the tier-2 supply chain link to SEMI-060 at PL-02.  

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT p.PLANT_ID, p.PLANT_NM, p.COUNTRY, (SELECT COUNT(*) FROM dbo.PLANT_MATERIAL pm WHERE pm.PLANT_ID=p.PLANT_ID) n_mat, (SELECT COUNT(*) FROM dbo.PLANT_MATERIAL pm WHERE pm.PLANT_ID=p.PLANT_ID AND (pm.MATERIAL_ID LIKE 'RM-%' OR pm.MATERIAL_ID LIKE 'CMP-%')) n_rm_cmp FROM dbo.PLANT p"}
  - → {"platform": "fabric", "columns": ["PLANT_ID", "PLANT_NM", "COUNTRY", "n_mat", "n_rm_cmp"], "rows": [["PL-01", "Riverside Sterile Operations", "US", 10, 0], ["PL-02", "Lakeview Ophthalmics Plant", "US", 5, 0], ["PL-03", "Harborside Solutions Plant", "US", 720, 0], ["PL-04", "Kilbride Sterile Plant", "IE", 669, 0]], "row_count": 4, "truncated": false, "elapsed_s": 1.05}
- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT b.PARENT_MATERIAL_ID, b.CHILD_MATERIAL_ID, b.QTY_PER, b.EFF_FROM, b.EFF_TO FROM dbo.BOM b WHERE b.CHILD_MATERIAL_ID IN ('RM-103','CMP-320','SEMI-044','SEMI-045','SEMI-060') ORDER BY b.CHILD_MATERIAL_ID"}
  - → {"platform": "fabric", "columns": ["PARENT_MATERIAL_ID", "CHILD_MATERIAL_ID", "QTY_PER", "EFF_FROM", "EFF_TO"], "rows": [["SEMI-060", "CMP-320", "0.100000", "2021-04-02", "9999-12-31"], ["CMP-320", "RM-103", "0.300000", "2023-08-12", "9999-12-31"], ["SEMI-044", "RM-103", "0.020000", "2023-06-22", "9999-12-31"], ["SEMI-045", "RM-103", "0.020000", "2020-07-29", "9999-12-31"], ["FILL-1001", "SEMI-044 …
### Turn 8
> 💭 I'm tracing where RM-103 flows since S-103 ships to PL-01 and PL-02, which suggests RM-103 reaches PL-02 for the Oculon chain, possibly via CMP-320 even though that compound is made by CDMOs S-202/S-203 — so PL-02 may produce CMP-320 in-house or consign RM-103 to the CDMO. Either way, the Oculon pathway at PL-02 depends on RM-103 supply.  Since S-111 isn't approved for PL-02, coverage is only partial: PL-01's Lacrivia and Cyclosporine are protected, but Oculon at PL-02 isn't. Neither the "fully covered" nor "no coverage anywhere" condition applies cleanly, so this falls outside the standard process path, meaning I need to reason through the graph manually and flag this case.  My plan is to raise a PR with S-111 for PL-01 to cover Lacrivia and Cyclosporine, while treating Oculon at PL-02 as disrupted — checking DC stock against safety stock for its finished packs and allocating only where …

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT b.PARENT_MATERIAL_ID, b.CHILD_MATERIAL_ID, b.QTY_PER FROM dbo.BOM b WHERE b.PARENT_MATERIAL_ID IN ('FG-1001','FG-1002','FG-1003','FG-2001','FG-2002') AND b.EFF_TO >= '2026-09-30' AND b.CHILD_MATERIAL_ID LIKE 'FILL-%'"}
  - → {"platform": "fabric", "columns": ["PARENT_MATERIAL_ID", "CHILD_MATERIAL_ID", "QTY_PER"], "rows": [["FG-1001", "FILL-1001", "1.000000"], ["FG-1002", "FILL-1002", "1.000000"], ["FG-1003", "FILL-1003", "1.000000"], ["FG-2001", "FILL-2001", "1.000000"], ["FG-2002", "FILL-2002", "1.000000"]], "row_count": 5, "truncated": false, "elapsed_s": 1.45}
- 🔧 `run_sql` {"platform": "fabric", "sql": "WITH latest AS (SELECT DC_ID, MATERIAL_ID, MAX(SNAPSHOT_DT) sd FROM dbo.DC_INV WHERE MATERIAL_ID IN ('FG-1001','FG-1002','FG-1003','FG-2001','FG-2002') GROUP BY DC_ID, MATERIAL_ID)\nSELECT i.DC_ID, i.MATERIAL_ID, i.SNAPSHOT_DT, i.ON_HAND_UNITS, i.SAFETY_STOCK_UNITS,\n (SELECT SUM(s.UNITS) FROM dbo.WHSLR_SHIP s WHERE s.DC_ID=i.DC_ID AND s.MATERIAL_ID=i.MATERIAL_ID AND …
  - → {"platform": "fabric", "columns": ["DC_ID", "MATERIAL_ID", "SNAPSHOT_DT", "ON_HAND_UNITS", "SAFETY_STOCK_UNITS", "ship28"], "rows": [["DC-CENTRAL", "FG-1001", "2026-09-25", 677, 314, 609], ["DC-EAST", "FG-1001", "2026-09-25", 46, 471, 1027], ["DC-WEST", "FG-1001", "2026-09-25", 593, 261, 408], ["DC-CENTRAL", "FG-1002", "2026-09-25", 351, 155, 291], ["DC-EAST", "FG-1002", "2026-09-25", 34, 233, 423 …
### Turn 9
> 💭 Oculon stays above safety stock everywhere, so it's not a concern. Lacrivia's FG-1001/1002 dip below safety stock at DC-EAST, but since S-111 at PL-01 qualifies as an alternate supplier, BR-ALLOC-02 says this shouldn't trigger allocation since the disruption doesn't actually interrupt supply — though I'm noting the shortage still physically exists at DC-EAST regardless of that rule.  

- 🔧 `get_lead_times` {"material_id": "RM-103", "finished_good": "FG-2001"}
  - → {"from_material":"RM-103","to_finished_good":"FG-2001","stages":[{"material":"RM-103","name":"Glycerin USP","type":"RAW","transit_days":7,"make_days":0,"qc_days":0,"note":null,"source":"MES standard times (default)","stage_days":7,"cumulative_days":7},{"material":"CMP-320","name":"Buffer/preservative concentrate","type":"COMPONENT","transit_days":3,"make_days":4,"qc_days":3,"note":null,"source":"M …
- 🔧 `get_lead_times` {"material_id": "RM-103", "finished_good": "FG-1001"}
  - → {"from_material":"RM-103","to_finished_good":"FG-1001","stages":[{"material":"RM-103","name":"Glycerin USP","type":"RAW","transit_days":7,"make_days":0,"qc_days":0,"note":null,"source":"MES standard times (default)","stage_days":7,"cumulative_days":7},{"material":"SEMI-044","name":"Cyclosporine 0.1% bulk emulsion","type":"SEMI","transit_days":0,"make_days":3,"qc_days":5,"note":null,"source":"MES s …
- 🔧 `get_reference` {"set_name": "supply_contracts"}
  - → [{"account_id":"AC00117","account":"Northfield Health System","tier":"A","expires":"2027-03-31","source":"contract-management system (outside the warehouses)"},{"account_id":"AC00038","account":"Oak Hollow Health System","tier":"A","expires":"2027-06-30","source":"contract-management system (outside the warehouses)"},{"account_id":"AC00059","account":"Riverbend Health System","tier":"A","expires": …
- 🔧 `get_reference` {"set_name": "dc_service_regions"}
  - → [{"dc":"DC-CENTRAL","states":["IL","TX","MN","CO"]},{"dc":"DC-EAST","states":["NY","NJ","PA","MA","FL","GA","NC","OH"]},{"dc":"DC-WEST","states":["AZ","CA","WA"]}]
### Turn 10
> 💭 Looking at the delay's impact on PO000210, I see Lacrivia and Cyclosporine at PL-01 are covered by approved supplier S-111, so I should raise a PR for PL-01, while Oculon at PL-02 lacks coverage and gets interrupted. Checking DC stock, Oculon is above safety stock everywhere so no allocation applies per process, and I'm calculating days of supply for DC-WEST's FG-2002 at roughly 30 days.  Since subsequent POs (211-213) scheduled for later dates likely still arrive on time, the actual disruption may be contained to just this one shipment rather than compounding further delays. I'm checking whether Lacrivia at DC-EAST falls below safety stock thresholds, which would trigger the allocation rule even though Oculon doesn't qualify.  Moving to notifications, SDR-4.1 applies since no allocation is needed here, which means I need to identify which DCs count as affected — since all three DCs stoc …

- 🔧 `get_context` {"question": "13-week TRx by top-level contracted account (health system rollup) and state for NDCs 99101030325, 99101030350, 99101010105, 99101010110, 99101020205", "role": "SUPPLY_PLANNER", "focus": ["customer definition", "TRx by account", "account state"]}
  - → {"concepts":[{"aligned_with":["FHIR: MedicationRequest / MedicationDispense"],"related":["Prescription -FOR-> PackagedProduct","Prescription -WRITTEN_BY-> Prescriber","Prescription -COVERED_BY-> Plan","Patient -FILLS-> Prescription"],"concept":"Prescription","definition":"Dispensed prescriptions, counted as TRx (total) and NRx (new-to-brand). The unit of demand and market share."},{"aligned_with": …
### Turn 11
> 💭 I need to query TRx grouped by top-level account hierarchy up to three levels, and by DC using the clinic account's state per the regional business rules. I'll pull 13 weeks of contracted accounts' Oculon TRx by DC, rolling clinic accounts up to hospital and then IDN using a coalesce on grandparent, parent, or self.  

- 🔧 `run_sql` {"platform": "snowflake", "sql": "WITH wk AS (SELECT DISTINCT WK_END_DT FROM PHARMA_DEMO.RAW_3P.RXT_WKLY ORDER BY WK_END_DT DESC LIMIT 13),\nrx AS (SELECT r.PROD_NDC11, r.TRX_QTY, a.STATE, COALESCE(gp.ACCOUNT_ID, p.ACCOUNT_ID, a.ACCOUNT_ID) TOP_ID\n FROM PHARMA_DEMO.RAW_3P.RXT_WKLY r JOIN wk ON wk.WK_END_DT=r.WK_END_DT\n JOIN PHARMA_DEMO.CORE.PRESCRIBER pr ON pr.PRSCRBR_ME=r.PRSCRBR_ME\n JOIN PHAR …
  - → {"platform": "snowflake", "columns": ["DC", "TOP_ID", "PROD_NDC11", "TRX13"], "rows": [["DC-CENTRAL", "AC00001", "99101010105", 96], ["DC-CENTRAL", "AC00001", "99101010110", 56], ["DC-CENTRAL", "AC00001", "99101020205", 49], ["DC-CENTRAL", "AC00001", "99101030325", 24], ["DC-CENTRAL", "AC00001", "99101030350", 9], ["DC-CENTRAL", "AC00038", "99101010105", 225], ["DC-CENTRAL", "AC00038", "9910101011 …
### Turn 12
> 💭 I see all 5 contracted accounts span every DC, so I need to pull the wholesaler list from the WHSLR table along with shipments of the affected packs.  

- 🔧 `run_sql` ⚠️ error {"platform": "fabric", "sql": "SELECT s.DC_ID, s.WHSLR_ID, w.*, SUM(s.UNITS) units_13wk FROM dbo.WHSLR_SHIP s JOIN dbo.WHSLR w ON w.WHSLR_ID=s.WHSLR_ID WHERE s.MATERIAL_ID IN ('FG-2001','FG-2002') AND s.SHIP_DT > DATEADD(week,-13,'2026-09-30') GROUP BY s.DC_ID, s.WHSLR_ID, w.WHSLR_ID, w.WHSLR_NM ORDER BY s.DC_ID"}
  - → {"error": "('42000', \"[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Column 'dbo.WHSLR.REGION' is invalid in the select list because it is not contained in either an aggregate function or the GROUP BY clause. (8120) (SQLExecDirectW)\")"}
### Turn 13

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT s.DC_ID, s.WHSLR_ID, w.WHSLR_NM, s.MATERIAL_ID, SUM(s.UNITS) units_13wk FROM dbo.WHSLR_SHIP s JOIN dbo.WHSLR w ON w.WHSLR_ID=s.WHSLR_ID WHERE s.MATERIAL_ID IN ('FG-2001','FG-2002','FG-1001','FG-1002','FG-1003') AND s.SHIP_DT > DATEADD(week,-13,'2026-09-30') GROUP BY s.DC_ID, s.WHSLR_ID, w.WHSLR_NM, s.MATERIAL_ID ORDER BY s.DC_ID, s.WHSLR_ID, s.MATERIAL_ID"}
  - → {"platform": "fabric", "columns": ["DC_ID", "WHSLR_ID", "WHSLR_NM", "MATERIAL_ID", "units_13wk"], "rows": [["DC-CENTRAL", "W-03", "Bridgeport Wholesale Drug", "FG-1001", 931], ["DC-CENTRAL", "W-03", "Bridgeport Wholesale Drug", "FG-1002", 458], ["DC-CENTRAL", "W-03", "Bridgeport Wholesale Drug", "FG-1003", 485], ["DC-CENTRAL", "W-03", "Bridgeport Wholesale Drug", "FG-2001", 370], ["DC-CENTRAL", "W …
### Turn 14
> 💭 I need to figure out PL-01's share of the delayed RM-103 PO by tracing consumption through the BOM chain — calculating RM-103 usage per finished good unit across FG-1001 (which consumes it via FILL-1001 and SEMI-044) and checking if FG-1002 has any RM-103 dependency at all.  For need_by, I'm working backward from S-111's typical lead time (~23 days based on PO000228) plus transit, landing on 2026-10-10 as a reasonable target. For PL-02, since S-111 isn't qualified there, I'll flag that as a separate action: escalate to Procurement/Supplier Quality to get S-111 qualified for that site.  For allocation decisions, Oculon stays above safety stock at all DCs so no allocation triggers under SDR-2.4, while Lacrivia at DC-EAST sits below safety stock but is covered by an alternate supplier, so it doesn't get allocated under BR-ALLOC-02 — though I should still flag that DC-EAST shortage to the Su …

- 🔧 `create_purchase_requisition` {"material_id": "RM-103", "supplier_id": "S-111", "quantity": 2760, "ship_to_plant": "PL-01", "need_by": "2026-10-10", "reason": "S-103 (Castellan) will ship RM-103 PO000210 (3,300 units, promised 2026-10-03) ~4 weeks late (~2026-10-31). S-111 (Kingsley) is qualified (SUPPLIER_MATERIAL) and portal-APPROVED/ACTIVE for RM-103 at PL-01 only. This PR covers PL-01's estimated share (~84% by RM-103 cons …
  - → {"pr_id": "PR-76D0D3D2", "status": "created"}
### Turn 15

- 🔧 `create_escalation_case` {"owner": "Procurement / Supplier Quality", "subject": "RM-103 delay (S-103 PO000210, +4 wks): no qualified alternate for PL-02 (Oculon)", "details": "S-103 Castellan Excipients will ship RM-103 Glycerin USP PO000210 (3,300 units, promised 2026-10-03) about 4 weeks late (~2026-10-31). Open S-103 RM-103 POs PO000211/212/213 (promised 10-10, 10-18, 10-25) should be confirmed as unaffected.\nAlternat …
  - → {"case_id": "CASE-42747E0B", "status": "open", "owner": "Procurement / Supplier Quality"}
- 🔧 `create_escalation_case` {"owner": "Trade Relations", "subject": "Wholesaler notice: RM-103 supply delay \u2013 Oculon (and Lacrivia/Cyclosporine OS) supply risk", "details": "EDI gateway has no API (process SDR-4.2), so please send this notice to the wholesalers served by all three DCs: W-01 Keystone and W-02 Atlas (DC-EAST), W-03 Bridgeport and W-04 Heartland (DC-CENTRAL), W-05 Pacific Crest and W-06 Sierra (DC-WEST). \ …
  - → {"case_id": "CASE-588193C6", "status": "open", "owner": "Trade Relations"}
- 🔧 `create_escalation_case` {"owner": "Supply Planning Lead", "subject": "Review: RM-103 disruption handled outside process path (partial alternate coverage); DC-EAST Lacrivia below safety stock", "details": "S-103 RM-103 PO000210 is ~4 weeks late. At decision SDR-2.1, the alternate S-111 is approved for PL-01 but not PL-02. That matches neither process condition ('approved for every plant' / 'not available for any plant'),  …
  - → {"case_id": "CASE-3A50C560", "status": "open", "owner": "Supply Planning Lead"}
### Turn 16
> Now the account-team notices for the five contracted accounts (all have TRx of the affected NDCs at all three DCs).

- 🔧 `notify_account_team` {"account_id": "AC00117", "subject": "Supply notice: Oculon supply risk from RM-103 delay \u2013 no allocation", "message": "Northfield Health System (Tier A): Supplier S-103 will ship a glycerin lot (RM-103) about 4 weeks late. Affected: Oculon 0.005% 2.5 mL (99101-0303-25) and 5 mL (99101-0303-50). Lacrivia 5/10 mL and Cyclosporine OS 0.05% are covered by a qualified alternate supplier. Allocati …
  - → {"task_id": "CRM-52682B61", "status": "open"}
- 🔧 `notify_account_team` {"account_id": "AC00038", "subject": "Supply notice: Oculon supply risk from RM-103 delay \u2013 no allocation", "message": "Oak Hollow Health System (Tier A): Supplier S-103 will ship a glycerin lot (RM-103) about 4 weeks late. Affected: Oculon 0.005% 2.5 mL (99101-0303-25) and 5 mL (99101-0303-50). Lacrivia 5/10 mL and Cyclosporine OS 0.05% are covered by a qualified alternate supplier. Allocati …
  - → {"task_id": "CRM-F17EC191", "status": "open"}
- 🔧 `notify_account_team` {"account_id": "AC00059", "subject": "Supply notice: Oculon supply risk from RM-103 delay \u2013 no allocation", "message": "Riverbend Health System (Tier A): Supplier S-103 will ship a glycerin lot (RM-103) about 4 weeks late. Affected: Oculon 0.005% 2.5 mL (99101-0303-25) and 5 mL (99101-0303-50). Lacrivia 5/10 mL and Cyclosporine OS 0.05% are covered by a qualified alternate supplier. Allocatio …
  - → {"task_id": "CRM-7AE54E5F", "status": "open"}
- 🔧 `notify_account_team` {"account_id": "AC00001", "subject": "Supply notice: Oculon supply risk from RM-103 delay \u2013 no allocation", "message": "Clearview Health System (Tier B): Supplier S-103 will ship a glycerin lot (RM-103) about 4 weeks late. Affected: Oculon 0.005% 2.5 mL (99101-0303-25) and 5 mL (99101-0303-50). Lacrivia 5/10 mL and Cyclosporine OS 0.05% are covered by a qualified alternate supplier. Allocatio …
  - → {"task_id": "CRM-A1C297BC", "status": "open"}
- 🔧 `notify_account_team` {"account_id": "AC00138", "subject": "Supply notice: Oculon supply risk from RM-103 delay \u2013 no allocation", "message": "Sunridge Health System (Tier B): Supplier S-103 will ship a glycerin lot (RM-103) about 4 weeks late. Affected: Oculon 0.005% 2.5 mL (99101-0303-25) and 5 mL (99101-0303-50). Lacrivia 5/10 mL and Cyclosporine OS 0.05% are covered by a qualified alternate supplier. Allocation …
  - → {"task_id": "CRM-521B2183", "status": "open"}
### Turn 17
> 💭 I've confirmed the 5 contracted accounts come solely from supply_contracts, matching the requirement to cover each contracted account. That satisfies the condition, so I'm ready to wrap up this check.  

- 🔧 `log_execution` {}
  - → {"trace_id":"169fca5d-6f68-49d3-a5ba-b25022cdff95","followed":["SDR-1.2","SDR-2.1","SDR-2.4","SDR-2.2","SDR-4.2","SDR-4.1"],"seeded_asset":"KA-169FCA5D"}

## Final report

I've handled the S-103 delay. The backup glycerin supplier (S-111) can only ship to one of our two plants, so I ordered from it for that plant and sent the other plant's gap to Procurement / Supplier Quality. No stock allocation is needed today, because no pack hit by this delay is below safety stock at any DC.

**This run is flagged for human review.** The process only covers two cases: a backup supplier approved for every plant that uses the material, or for none. Here it's approved for one plant and not the other. No trusted playbook covers this, and the search that also returns unapproved playbooks found none, so I worked out the path myself.

**What I found**
- **The late order:** The next S-103 shipment of RM-103 (glycerin) is PO000210: 3,300 units, promised 2026-10-03, now about 2026-10-31. S-103 has three more open RM-103 orders (PO000211–213, due 10-10 to 10-25). I assumed they ship on time.
- **Products affected:** The glycerin goes into five products:
  - Lacrivia 5 mL and 10 mL, and Cyclosporine 0.05% 5 mL, made at plant PL-01.
  - Oculon 2.5 mL and 5 mL, made at plant PL-02. Their path runs through a component made by contract manufacturers S-202 and S-203.
- **Backup supplier:** S-111 is qualified, active and not on hold, but approved to ship to PL-01 only. PL-01 is covered; PL-02 (Oculon) is not.
- **DC stock (snapshot 2026-09-25):**
  - Oculon is above safety stock at every DC, so the process says no allocation.
  - Oculon is still tight: the 5 mL pack at DC-WEST has about 31 days of supply. Both Oculon packs at DC-CENTRAL have about 35–37 days.
  - Lacrivia 5 mL (46 units vs 471 safety stock) and 10 mL (34 vs 233) are already below safety stock at DC-EAST. The backup supplier covers their plant, so the rules exclude them from allocation under this delay.
- **When supply recovers:** Oculon made from the late glycerin reaches the DCs about 46 days after S-103 ships, so around 2026-12-16. Lacrivia takes 37 days from whenever S-111 ships.
- **Substitutes:** Oculon has no approved company substitute. Both Oculon pack sizes are above safety stock, so customers can be offered the other size.

**Actions taken**

| Action | ID |
|---|---|
| Purchase requisition to S-111 for RM-103: 2,760 units to PL-01, needed by 2026-10-10 (the original arrival date) | PR-76D0D3D2 |
| Case to Procurement / Supplier Quality: speed up S-103 or get PL-02's share (about 540 units) shipped early, look at approving S-111 for PL-02, and check glycerin and component buffers at PL-02, S-202 and S-203 | CASE-42747E0B |
| Case to Trade Relations: delay notice for wholesalers W-01 to W-06. The EDI gateway has no API, so the process hands this to them. | CASE-588193C6 |
| Case to the Supply Planning lead: review of this off-process path, plus a decision on the Lacrivia shortage at DC-EAST | CASE-3A50C560 |
| Account-team notices (no allocation, recovery around Dec 16, no Oculon substitute) for Northfield (AC00117), Oak Hollow (AC00038), Riverbend (AC00059), Clearview (AC00001) and Sunridge (AC00138) | CRM-52682B61, CRM-F17EC191, CRM-7AE54E5F, CRM-A1C297BC, CRM-521B2183 |

**Not done, and why**
- **No allocation or approval request:** no pack hit by this delay is below safety stock.
- **Lacrivia at DC-EAST:** I didn't allocate it or move stock from DC-CENTRAL or DC-WEST, where both packs are well above safety stock. It's an existing shortage, not caused by this delay, and a transfer between DCs needs the Supply Planning lead's approval. That's in CASE-3A50C560.
- **Cyclosporine as a Lacrivia substitute at DC-EAST:** I didn't offer it. It uses the same glycerin, so whether it counts as "constrained" is the lead's call.
- **No order to S-111 for PL-02:** S-111 isn't approved to ship there.
- **Wholesaler stock not checked:** that feed doesn't start until Q4 2026.

**Assumptions**
- **Requisition size:** 2,760 units is PL-01's estimated share of the late order, about 84%. I worked it out from the last 13 weeks of shipments of each product and the glycerin each one uses.
- **Customers:** I notified only the five accounts with supply contracts. All five have prescriptions for the affected products in all three DC regions.

**Knowledge-layer sources:** process Supply Disruption Response, steps SDR-1.1 to 4.2; rules BR-ALLOC-01/02, BR-APPR-01, BR-SUB-01/02, BR-LEAD-01, BR-CUST-01, BR-REGION-01 and POL-DUA-01 (no patient-level data used); the supply-exposure trace and lead-time stages; and the supply_contracts and dc_service_regions reference sets.

## Final state of the ops store (sandbox)

- **Requisition** PR-76D0D3D2 · RM-103 from S-111 → PL-01 · qty 2760
- **Case** CASE-42747E0B → Procurement / Supplier Quality: RM-103 delay (S-103 PO000210, +4 wks): no qualified alternate for PL-02 (Oculon)
- **Case** CASE-588193C6 → Trade Relations: Wholesaler notice: RM-103 supply delay – Oculon (and Lacrivia/Cyclosporine OS) supply risk
- **Case** CASE-3A50C560 → Supply Planning Lead: Review: RM-103 disruption handled outside process path (partial alternate coverage); DC-EAST Lacrivia below safety stock
- **CRM tasks** (5): AC00001, AC00038, AC00059, AC00117, AC00138
