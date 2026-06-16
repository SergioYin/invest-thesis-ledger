# Decision Review Pack: Leveraged ETF Discipline Ledger

> This packet organizes existing ledger data for review. It is not investment advice and does not recommend buying, selling, or holding any asset.

## Thesis Status

- Ledger ID: leveraged-etf-discipline
- Updated: 2026-05-19
- Asset: LEV2X (Generic 2x Equity Index ETF)
- Type: fund
- Status: needs-review
- Review Priority: high
- Review Score: 13
- Next Action: Review high-severity risks and update mitigation evidence.

### Latest Review

- Date: 2026-05-19
- Decision: policy
- Summary: Added catalyst requirements so trade setup, holding period, and macro event risk are checked before entry.
- Drift: Workflow expanded from static risk reminder to pre-trade evidence gate.
- Sources: [S1]

### Review Drivers

- high_severity_risks: 2 high-severity risk(s) need human review. (count: 2; score: 6; items: R1, R2)
- upcoming_open_catalysts: 2 upcoming or open catalyst(s) remain unresolved. (count: 2; score: 2; items: CAT2, CAT1)
- open_checklist: 3 checklist item(s) remain open. (count: 3; score: 3; items: C1, C2, C3)
- open_position_rules: 2 position rule(s) remain open. (count: 2; score: 2; items: P1, P2)

## Review Evidence

- Evidence is copied from ledger source references only; no market data or outside lookup was added.
- Unsupported items are information gaps for a reviewer to resolve before relying on the packet.

### Evidence Map

- assumption A1: supported; sources: [S1]
- assumption A2: supported; sources: [S2]
- catalyst CAT1: unsupported; sources: none
- catalyst CAT2: supported; sources: [S1]
- position_rule P1: supported; sources: [S1], [S2]
- position_rule P2: supported; sources: [S1]
- review REV1:2026-05-12: supported; sources: [S1], [S2]
- review REV2:2026-05-19: supported; sources: [S1]
- risk R1: supported; sources: [S1], [S2]
- risk R2: supported; sources: [S1]

### Source Index

- [S1] Leveraged and inverse ETF risk bulletin. Investor Education Desk, 2026-03-15. https://example.com/leveraged-etf-risk-bulletin
- [S2] Volatility drag illustration. Portfolio Research Notes, 2026-04-05. https://example.com/volatility-drag

## Evidence Freshness

- Status: partial
- Quality Score: 94
- Tracked Items: 10
- Supported Items: 9
- Unsupported Items: 1
- Sources: 2
- Stale Sources: 0
- Unused Sources: 0
- No stale sources detected.
- Unsupported catalyst CAT1

## Risks and Catalysts

### High Risks

- R1: Volatility drag (severity: high; probability: high; mitigation: Use only with explicit holding-period limit and daily review.; sources: [S1], [S2])
- R2: Oversized exposure (severity: high; probability: medium; mitigation: Cap notional exposure before order entry.; sources: [S1])

### Open Catalysts

- CAT2: Macro event calendar supports a time-boxed tactical setup. (date: 2026-06-10) (status: required; sources: [S1])
- CAT1: Index breaks above predefined technical level. (window: before entry) (status: required; sources: none)

## Next Review Questions

- [ ] Q1: Does the latest review decision still support the contemplated action?
- [ ] Q2: Are all high-severity risks understood with current mitigation evidence?
- [ ] Q3: Have open catalysts been checked for new source-backed status changes?
- [ ] Q4: Do open position rules permit the proposed exposure?
- [ ] Q5: Are stale, unused, or unsupported evidence gaps acceptable before action?
- [ ] Q6: What evidence would falsify the action after execution?

## Command Provenance

- Command: `python -m invest_thesis_ledger decision-review-pack <ledger.json> --output <review-pack.md> --json-output <review-pack.json>`
- Workflow: single-ledger decision-review-pack
- Input Ledger: <ledger.json>
- Markdown Output: <review-pack.md>
- JSON Output: <review-pack.json>

## Boundary

- This packet organizes existing ledger data for review. It is not investment advice and does not recommend buying, selling, or holding any asset.

## Sources

- [S1] Leveraged and inverse ETF risk bulletin. Investor Education Desk, 2026-03-15. https://example.com/leveraged-etf-risk-bulletin
- [S2] Volatility drag illustration. Portfolio Research Notes, 2026-04-05. https://example.com/volatility-drag
