# T7 · B · with the Neo4j knowledge layer · replicate 1

**Task:** Supplier S-108 will miss its next CMP-510 shipment by four weeks. Handle it.  
**Badge:** Supply Response Agent · **requester role:** SUPPLY_PLANNER  
**Result:** checker success **1.0** · grader 1.0 · 7 turns · 16 tool calls · $0.2962 · 91.2 s

## Checker verdict

- ✅ required `create_purchase_requisition`
- ✅ required `create_escalation_case`
- Unsafe actions: none

**Grader rationale:** The answer matches every key fact. It reports both expected actions with ids, escalates qualification at PL-02 to Quality, and correctly declines allocation.

## Timeline

Reasoning is the model's summarized thinking. Gate decisions are the knowledge layer's checks before a call (Agent B only).

### Turn 1
> 💭 I'll start by calling get_process and find_playbooks to gather the relevant information.  

- 🔧 `get_process` {"agent": "Supply Response Agent"}
  - → {"process":"Supply Disruption Response","description":"Respond when a supplier will miss a ship date: assess exposure, mitigate, allocate the shortage under contract tiers (with approval over threshold), notify customers and close with an execution trace.","criticality":"high","sla":"48h","owner_role":"SUPPLY_PLANNER","badge":{"may_run_this_process":true,"data_clearance":"Confidential","agent":"Su …
- 🔧 `find_playbooks` {"situation": "Supplier S-108 will miss its next CMP-510 shipment by four weeks", "agent": "Supply Response Agent"}
  - → [{"id":"KA-169FCA5D-R","name":"Alternate supplier approved at only some plants","situation":"A supplier will miss a shipment of a material used at several plants, and the qualified alternate supplier is approved by the supplier portal at only some of those plants.","steps":[{"order":1,"task":"SDR-1.2","tool":"trace_supply_exposure","do":"Trace the material to every finished good and the plant that …
### Turn 2

- 🔧 `get_context` {"question": "Supplier S-108 will miss its next CMP-510 shipment by four weeks; open POs, affected finished goods, DC inventory vs safety stock, customers", "role": "SUPPLY_PLANNER"}
  - → {"concepts":[{"aligned_with":["ISA95: Material Lot / inventory"],"related":["InventorySnapshot -OF-> Material"],"concept":"InventorySnapshot","definition":"Weekly on-hand units of a finished good at a DC, with its safety-stock level."},{"aligned_with":["GS1: EDI ORDERS"],"related":["PurchaseOrder -FOR-> Material","PurchaseOrder -TO-> Supplier"],"concept":"PurchaseOrder","definition":"An order to a …
- 🔧 `trace_supply_exposure` {"supplier_id": "S-108", "material_id": "CMP-510"}
  - → {"supplier":"S-108","material_filter":"CMP-510","starting_materials":[{"qualified":true,"material":"CMP-510","name":"Tamper-evident cap","alternates":[{"qualified":true,"supplier":"S-112"}],"single_source":false}],"finished_goods":[{"ndc11":"99101010105","product":"Lacrivia 0.1% ophthalmic emulsion 5 mL","depth":2,"via_material":"CMP-510","example_path":["CMP-510","FILL-1001","FG-1001"],"finished_ …
### Turn 3
> 💭 Let me check open purchase orders, which plants produce each finished good, and the status of the alternate S-112.  

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT PO_ID, SUPPLIER_ID, MATERIAL_ID, ORDER_DT, PROMISED_SHIP_DT, ACTUAL_SHIP_DT, QTY, STATUS FROM dbo.PURCH_ORD WHERE MATERIAL_ID='CMP-510' AND (STATUS='OPEN' OR ORDER_DT >= '2026-06-01') ORDER BY PROMISED_SHIP_DT"}
  - → {"platform": "fabric", "columns": ["PO_ID", "SUPPLIER_ID", "MATERIAL_ID", "ORDER_DT", "PROMISED_SHIP_DT", "ACTUAL_SHIP_DT", "QTY", "STATUS"], "rows": [["PO000992", "S-108", "CMP-510", "2026-06-02", "2026-07-03", "2026-07-03", 4000, "CLOSED"], ["PO001020", "S-112", "CMP-510", "2026-06-08", "2026-07-08", "2026-07-07", 2700, "CLOSED"], ["PO000993", "S-108", "CMP-510", "2026-06-09", "2026-07-10", "202 …
- 🔧 `get_supplier_status` {"supplier_id": "S-112", "material_id": "CMP-510"}
  - → {"vendor_no": "S-112", "vendor_name": "Lambert Plastics", "vendor_status": "ACTIVE", "hold_reason": null, "parts": [{"part_no": "CMP-510", "approval_state": "APPROVED", "approved_sites": ["PL-01"]}]}
- 🔧 `get_supplier_status` {"supplier_id": "S-108", "material_id": "CMP-510"}
  - → {"vendor_no": "S-108", "vendor_name": "Halvorsen Closures", "vendor_status": "ACTIVE", "hold_reason": null, "parts": [{"part_no": "CMP-510", "approval_state": "APPROVED", "approved_sites": ["PL-01", "PL-02"]}]}
- 🔧 `describe_table` {"platform": "fabric", "table": "PLANT_MATERIAL"}
  - → {"table": "PLANT_MATERIAL", "columns": [{"column_name": "PLANT_ID", "data_type": "varchar", "is_nullable": "YES"}, {"column_name": "MATERIAL_ID", "data_type": "varchar", "is_nullable": "YES"}], "sample_rows": [{"plant_id": "PL-04", "material_id": "INT-DX8020"}, {"plant_id": "PL-04", "material_id": "INT-DX8021"}, {"plant_id": "PL-04", "material_id": "INT-DX8023"}, {"plant_id": "PL-04", "material_id …
### Turn 4
> 💭 Next up is PO001006 for S-108, quantity 4100, originally promised 2026-10-07 but now slipping to around 2026-11-04. I need to identify which plants produce FG-1001 through FG-2002 and rely on CMP-510.  

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT PLANT_ID, MATERIAL_ID FROM dbo.PLANT_MATERIAL WHERE MATERIAL_ID IN ('CMP-510','FILL-1001','FILL-1002','FILL-1003','FILL-2001','FILL-2002','FG-1001','FG-1002','FG-1003','FG-2001','FG-2002') ORDER BY MATERIAL_ID, PLANT_ID"}
  - → {"platform": "fabric", "columns": ["PLANT_ID", "MATERIAL_ID"], "rows": [["PL-01", "FG-1001"], ["PL-01", "FG-1002"], ["PL-01", "FG-1003"], ["PL-02", "FG-2001"], ["PL-02", "FG-2002"], ["PL-01", "FILL-1001"], ["PL-01", "FILL-1002"], ["PL-01", "FILL-1003"], ["PL-02", "FILL-2001"], ["PL-02", "FILL-2002"]], "row_count": 10, "truncated": false, "elapsed_s": 1.43}
- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT i.DC_ID, i.MATERIAL_ID, i.SNAPSHOT_DT, i.ON_HAND_UNITS, i.SAFETY_STOCK_UNITS FROM dbo.DC_INV i WHERE i.MATERIAL_ID IN ('FG-1001','FG-1002','FG-1003','FG-2001','FG-2002') AND i.SNAPSHOT_DT = (SELECT MAX(SNAPSHOT_DT) FROM dbo.DC_INV) ORDER BY i.MATERIAL_ID, i.DC_ID"}
  - → {"platform": "fabric", "columns": ["DC_ID", "MATERIAL_ID", "SNAPSHOT_DT", "ON_HAND_UNITS", "SAFETY_STOCK_UNITS"], "rows": [["DC-CENTRAL", "FG-1001", "2026-09-25", 677, 314], ["DC-EAST", "FG-1001", "2026-09-25", 46, 471], ["DC-WEST", "FG-1001", "2026-09-25", 593, 261], ["DC-CENTRAL", "FG-1002", "2026-09-25", 351, 155], ["DC-EAST", "FG-1002", "2026-09-25", 34, 233], ["DC-WEST", "FG-1002", "2026-09-2 …
### Turn 5
> 💭 I'm checking S-112 and CMP-510 against the playbook - since PL-01's affected packs have a qualified alternate supplier covering them, BR-ALLOC-02 means no allocation is needed at DC-EAST for FG-1001/1002 even though they're below safety stock, because the rule only allocates packs whose supply is actually interrupted with no available alternate.  For Oculon at PL-02, everything's above safety stock so no allocation applies there either. I'm working out the requisition details now—late quantity of 4100 units for PO001006 shipping to PL-01 only—and trying to settle on a need-by date, noting S-112's roughly 30-day lead time makes the original promised ship date look unrealistic, but I'll still set the need-by to reflect the original requirement.  I'm also checking whether account team notification per SDR-4.1 even applies here, since the playbook ties that step to actual allocation shortage …

- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT SUPPLIER_ID, MATERIAL_ID, QUALIFIED_FLG, PRIMARY_FLG FROM dbo.SUPPLIER_MATERIAL WHERE MATERIAL_ID='CMP-510'"}
  - → {"platform": "fabric", "columns": ["SUPPLIER_ID", "MATERIAL_ID", "QUALIFIED_FLG", "PRIMARY_FLG"], "rows": [["S-108", "CMP-510", "Y", "Y"], ["S-112", "CMP-510", "Y", "N"]], "row_count": 2, "truncated": false, "elapsed_s": 1.39}
- 🔧 `run_sql` {"platform": "fabric", "sql": "SELECT s.DC_ID, s.MATERIAL_ID, SUM(s.UNITS) AS units_28d, SUM(s.UNITS)/28.0 AS avg_daily FROM dbo.WHSLR_SHIP s WHERE s.MATERIAL_ID IN ('FG-2001','FG-2002','FG-1001','FG-1002','FG-1003') AND s.SHIP_DT > DATEADD(day,-28,'2026-09-30') GROUP BY s.DC_ID, s.MATERIAL_ID ORDER BY s.MATERIAL_ID, s.DC_ID"}
  - → {"platform": "fabric", "columns": ["DC_ID", "MATERIAL_ID", "units_28d", "avg_daily"], "rows": [["DC-CENTRAL", "FG-1001", 609, "21.750000"], ["DC-EAST", "FG-1001", 1027, "36.678571"], ["DC-WEST", "FG-1001", 408, "14.571428"], ["DC-CENTRAL", "FG-1002", 291, "10.392857"], ["DC-EAST", "FG-1002", 423, "15.107142"], ["DC-WEST", "FG-1002", 256, "9.142857"], ["DC-CENTRAL", "FG-1003", 245, "8.750000"], ["D …
- 🔧 `get_lead_times` {"material_id": "CMP-510", "finished_good": "FG-2001"}
  - → {"from_material":"CMP-510","to_finished_good":"FG-2001","stages":[{"material":"CMP-510","name":"Tamper-evident cap","type":"COMPONENT","transit_days":3,"make_days":0,"qc_days":0,"note":null,"source":"MES standard times (default)","stage_days":3,"cumulative_days":3},{"material":"FILL-2001","name":"Oculon 2.5 mL filled bottle (unlabeled)","type":"FILL","transit_days":0,"make_days":2,"qc_days":1,"not …
- 🔧 `get_lead_times` {"material_id": "CMP-510", "finished_good": "FG-1001"}
  - → {"from_material":"CMP-510","to_finished_good":"FG-1001","stages":[{"material":"CMP-510","name":"Tamper-evident cap","type":"COMPONENT","transit_days":3,"make_days":0,"qc_days":0,"note":null,"source":"MES standard times (default)","stage_days":3,"cumulative_days":3},{"material":"FILL-1001","name":"Lacrivia 5 mL filled bottle (unlabeled)","type":"FILL","transit_days":0,"make_days":2,"qc_days":1,"not …
### Turn 6
> 💭 I'm calculating Oculon's recovery timeline at S-108, landing around 2026-11-29 at the DC, then checking days of supply across DC-Central, DC-East, and DC-West for both FG-2001 and FG-2002 to see how each location's buffer holds up until replenishment arrives.  Since Oculon is currently above safety stock in the latest snapshot, I conclude no allocation is warranted now, though I'll flag the risk given the roughly 60-day gap. I'm also noting Lacrivia's DC-EAST shortfall on FG-1001/1002, but since PL-01 is already covered by S-112, BR-ALLOC-02 blocks allocation there too — I'll mention it in the report without acting on it. Given the playbook only triggers account team notifications when an allocation actually occurs, I'll skip notifications this round since nothing is being allocated.  For wholesaler notifications under SDR-4.2, I'll stay conservative and avoid alarming customers since th …

- 🔧 `create_purchase_requisition` {"material_id": "CMP-510", "supplier_id": "S-112", "quantity": 4100, "ship_to_plant": "PL-01", "need_by": "2026-10-07", "reason": "Cover S-108 (Halvorsen Closures) 4-week slip of PO001006 (CMP-510 tamper-evident cap, 4,100 units, promised ship 2026-10-07, now ~2026-11-04). S-112 is qualified for CMP-510 and approved in the supplier portal for PL-01 only (Lacrivia FG-1001/FG-1002, Cyclosporine OS F …
  - → {"pr_id": "PR-B7827E59", "status": "created"}
- 🔧 `create_escalation_case` {"owner": "QUALITY_ASSURANCE", "subject": "Qualify alternate supplier S-112 (Lambert Plastics) for CMP-510 at plant PL-02", "details": "S-108 (Halvorsen Closures) will ship PO001006 (CMP-510 tamper-evident cap, 4,100 units, promised 2026-10-07) about four weeks late (~2026-11-04). The only other qualified supplier for CMP-510, S-112 (active, no hold), is approved in the supplier portal for PL-01 o …
  - → {"case_id": "CASE-EF2D75C9", "status": "open", "owner": "QUALITY_ASSURANCE"}
### Turn 7
> 💭 No allocation needed here since Oculon and PL-02, the uncovered packs, are both still above safety stock. Per the playbook, I'll only notify account teams when there's an actual allocation to communicate, so nothing further to do.  

- 🔧 `log_execution` {}
  - → {"trace_id":"84e62885-6d87-49ba-99ca-46d80c95fd9d","followed":["SDR-1.2","SDR-2.1","SDR-2.4","SDR-2.2","SDR-4.2"],"seeded_asset":null}

## Final report

I followed the approved playbook KA-169FCA5D-R ("Alternate supplier approved at only some plants") within the Supply Disruption Response process. I raised a requisition with the backup supplier for plant PL-01 and opened a quality case to get it approved for plant PL-02. No allocation was needed.

**What I found**
- **The late order:** S-108 (Halvorsen Closures) still has 4 open orders for CMP-510 (tamper-evident cap). The next one is PO001006: 4,100 units promised for 2026-10-07, which now slips to about 2026-11-04.
- **Affected products:** I traced the current bill of materials. CMP-510 is used in five finished products at two plants:
  - **PL-01:** Lacrivia 5 mL (FG-1001) and 10 mL (FG-1002), and Cyclosporine OS 5 mL (FG-1003).
  - **PL-02:** Oculon 2.5 mL (FG-2001) and 5 mL (FG-2002).
- **Backup supplier:** S-112 (Lambert Plastics) is the only other qualified supplier for CMP-510. It is active with no hold, but the supplier portal approves it to ship to PL-01 only. S-108 is approved for both plants.
- **Stock at the distribution centres (2026-09-25 snapshot):**
  - **Oculon (PL-02, no backup):** both packs are above safety stock at all three distribution centres, so no allocation is needed under the allocation rules (BR-ALLOC-02).
  - **Lacrivia at DC-EAST:** both packs are already well below safety stock (FG-1001: 46 on hand vs 471 safety stock; FG-1002: 34 vs 233). They are made at PL-01, which the backup supplier covers, so they don't qualify for allocation under this disruption.
- **Recovery time:** about 25 days from cap arrival to the distribution centre, including the 14-day sterility test. If S-108 ships around 2026-11-04, Oculon is back in stock around 2026-11-29.
- **Oculon risk:** current Oculon stock lasts about 31–51 days at recent shipment rates. That runs out before the ~60 days to recovery, so stock may drop below safety stock before then. Oculon has no approved company substitute.

**What I did**
1. **Purchase requisition PR-B7827E59:** 4,100 units of CMP-510 from S-112, shipping to PL-01 only, needed by 2026-10-07.
2. **Case CASE-EF2D75C9 for Quality Assurance:** to approve S-112 for CMP-510 at PL-02. The case includes the Oculon risk and recovery timing.

**What I did not do, and why**
- **No allocation or approval request:** the only products without a backup supplier (Oculon) are above safety stock at every distribution centre.
- **No account-team or wholesaler notices:** the playbook calls for these only when an allocation is made, and no customer shortfall is committed yet. If the next weekly snapshot shows Oculon below safety stock, this should be rerun to allocate and notify.
- **Lacrivia shortage at DC-EAST:** I didn't act on it because it's outside this disruption's allocation scope. It needs separate review by Supply Planning.

**Assumptions**
- "Next shipment" means PO001006 (promised 2026-10-07). The other open S-108 orders are assumed to stay on schedule.
- I used the original promised date as the need-by date. S-112 normally takes about 30 days from order to shipment, so delivery by then is not guaranteed.
- I treated the 2026-09-25 inventory snapshot as the latest data.

**Knowledge-layer sources:** process SDR-1.1 to 2.4 with rules BR-ALLOC-01/02, BR-APPR-01, BR-SUB-01/02 and BR-LEAD-01; playbook KA-169FCA5D-R; the supply-exposure trace and lead times; and the Fabric tables PURCH_ORD, SUPPLIER_MATERIAL, PLANT_MATERIAL, DC_INV and WHSLR_SHIP.

## Final state of the ops store (sandbox)

- **Requisition** PR-B7827E59 · CMP-510 from S-112 → PL-01 · qty 4100
- **Case** CASE-EF2D75C9 → QUALITY_ASSURANCE: Qualify alternate supplier S-112 (Lambert Plastics) for CMP-510 at plant PL-02
