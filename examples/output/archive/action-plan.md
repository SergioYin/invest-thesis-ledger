# Weekly Action Plan

> This is an educational research organization tool, not investment advice. It does not include market data.

- Ledgers: 2
- Ranked Actions: 2
- Now: 2
- This Week: 0
- Watch: 0

## Ranked Actions

| Rank | Cadence | Owner | Ticker | Ledger ID | Priority | Score | Action | Reason Codes | Source Warnings |
| ---: | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| 1 | now | TBD | LEV2X | leveraged-etf-discipline | high | 13 | Review high-severity risks and update mitigation evidence. | EA_SOURCE_QUALITY_WARNING, RQ_HIGH_SEVERITY_RISKS, RQ_OPEN_CHECKLIST, RQ_OPEN_POSITION_RULES, RQ_UPCOMING_OPEN_CATALYSTS, WL_LATEST_REVIEW_RECORDED, WL_NEAREST_OPEN_CATALYST | SOURCE_UNSUPPORTED_ITEM, SOURCE_UNSUPPORTED_ITEM, SOURCE_UNSUPPORTED_ITEM, SOURCE_UNSUPPORTED_ITEM |
| 2 | now | TBD | OKLO | oklo-ai-power | high | 10 | Review high-severity risks and update mitigation evidence. | EA_SOURCE_QUALITY_WARNING, RQ_HIGH_SEVERITY_RISKS, RQ_OPEN_CHECKLIST, RQ_OPEN_POSITION_RULES, RQ_UPCOMING_OPEN_CATALYSTS, WL_LATEST_REVIEW_RECORDED, WL_NEAREST_OPEN_CATALYST | SOURCE_UNSUPPORTED_ITEM, SOURCE_UNSUPPORTED_ITEM |

## Action Details

### 1. LEV2X - Leveraged ETF Discipline Ledger

- Owner: TBD
- Cadence: now
- Action: Review high-severity risks and update mitigation evidence.
- Source Quality Score: 81
- Reason Codes: EA_SOURCE_QUALITY_WARNING, RQ_HIGH_SEVERITY_RISKS, RQ_OPEN_CHECKLIST, RQ_OPEN_POSITION_RULES, RQ_UPCOMING_OPEN_CATALYSTS, WL_LATEST_REVIEW_RECORDED, WL_NEAREST_OPEN_CATALYST

#### Blockers

- CHECKLIST_OPEN: C1: Record entry price, stop, target, and expiry date before trade.
- CHECKLIST_OPEN: C2: Confirm no earnings, CPI, FOMC, or other event invalidates sizing.
- CHECKLIST_OPEN: C3: Review realized leverage and tracking after each close.
- EXPOSURE_OPEN_RULE: P1: Limit planned holding period to five trading days.
- EXPOSURE_OPEN_RULE: P2: Cap notional exposure before order entry.
- RISK_HIGH_SEVERITY: R1: Volatility drag
- RISK_HIGH_SEVERITY: R2: Oversized exposure

#### Source-Quality Warnings

- SOURCE_UNSUPPORTED_ITEM: catalyst CAT1 has no source reference.
- SOURCE_UNSUPPORTED_ITEM: checklist C1 has no source reference.
- SOURCE_UNSUPPORTED_ITEM: checklist C2 has no source reference.
- SOURCE_UNSUPPORTED_ITEM: checklist C3 has no source reference.

#### Next Checklist

- [ ] AP1: Confirm the latest review summary and update the ledger if it has drifted. (review_queue)
- [ ] AP2: Refresh or annotate source-quality warnings before relying on the plan. (evidence_audit)
- [ ] AP3: Review open risk, exposure, and catalyst records for source-backed status changes. (risk_exposure_catalyst)
- [ ] AP-RISK: Review high-severity risk IDs: R1, R2. (risk_payload)
- [ ] AP-CATALYST: Check open catalyst IDs: CAT2, CAT1. (catalyst_payload)
- [ ] AP-EXPOSURE: Resolve open exposure rule IDs: P1, P2. (exposure_payload)
- [ ] AP-CHECKLIST: Update open checklist IDs: C1, C2, C3. (review_queue)
- [ ] AP-SOURCES: Address source warning codes: SOURCE_UNSUPPORTED_ITEM. (evidence_audit)

### 2. OKLO - Oklo AI Power Demand Thesis

- Owner: TBD
- Cadence: now
- Action: Review high-severity risks and update mitigation evidence.
- Source Quality Score: 92
- Reason Codes: EA_SOURCE_QUALITY_WARNING, RQ_HIGH_SEVERITY_RISKS, RQ_OPEN_CHECKLIST, RQ_OPEN_POSITION_RULES, RQ_UPCOMING_OPEN_CATALYSTS, WL_LATEST_REVIEW_RECORDED, WL_NEAREST_OPEN_CATALYST

#### Blockers

- CHECKLIST_OPEN: C1: Confirm latest cash balance and expected burn.
- CHECKLIST_OPEN: C2: Map each announced customer to binding contract evidence.
- EXPOSURE_OPEN_RULE: P1: Keep status at watchlist until a dated licensing update is source-backed.
- EXPOSURE_OPEN_RULE: P2: Do not size from AI power narrative without named contract evidence.
- RISK_HIGH_SEVERITY: R1: Licensing delay

#### Source-Quality Warnings

- SOURCE_UNSUPPORTED_ITEM: checklist C1 has no source reference.
- SOURCE_UNSUPPORTED_ITEM: checklist C2 has no source reference.

#### Next Checklist

- [ ] AP1: Confirm the latest review summary and update the ledger if it has drifted. (review_queue)
- [ ] AP2: Refresh or annotate source-quality warnings before relying on the plan. (evidence_audit)
- [ ] AP3: Review open risk, exposure, and catalyst records for source-backed status changes. (risk_exposure_catalyst)
- [ ] AP-RISK: Review high-severity risk IDs: R1. (risk_payload)
- [ ] AP-CATALYST: Check open catalyst IDs: CAT2, CAT1, CAT3. (catalyst_payload)
- [ ] AP-EXPOSURE: Resolve open exposure rule IDs: P1, P2. (exposure_payload)
- [ ] AP-CHECKLIST: Update open checklist IDs: C1, C2. (review_queue)
- [ ] AP-SOURCES: Address source warning codes: SOURCE_UNSUPPORTED_ITEM. (evidence_audit)

