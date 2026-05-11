# Decision Memo: Leveraged ETF Discipline Ledger

> This is a research organization tool, not investment advice.

## Asset / Thesis Snapshot

- Ledger ID: leveraged-etf-discipline
- Updated: 2026-05-12
- Asset: LEV2X (Generic 2x Equity Index ETF)
- Type: fund
- Thesis: Leveraged ETFs can express short-term tactical views, but path dependency, volatility drag, and position sizing rules must dominate the decision process.

### Assumptions

- A1: The instrument is used for a defined short-term thesis rather than a long-term allocation. (confidence: high; sources: [S1])
- A2: Volatility conditions are reviewed before entry and daily while open. (confidence: medium; sources: [S2])

## Latest Review

- Date: 2026-05-19
- Decision: policy
- Summary: Added catalyst requirements so trade setup, holding period, and macro event risk are checked before entry.
- Drift: Workflow expanded from static risk reminder to pre-trade evidence gate.
- Sources: [S1]

## Broker View Summary

- Views: 0
- No broker ratings recorded.

## High Risks

- R1: Volatility drag (severity: high; probability: high; tags: leverage, volatility, path-dependency; mitigation: Use only with explicit holding-period limit and daily review.; sources: [S1], [S2])
- R2: Oversized exposure (severity: high; probability: medium; tags: sizing, leverage; mitigation: Cap notional exposure before order entry.; sources: [S1])

## Catalyst Checklist

- [ ] CAT2: Macro event calendar supports a time-boxed tactical setup. (date: 2026-06-10) (status: required; sources: [S1])
- [ ] CAT1: Index breaks above predefined technical level. (window: before entry) (status: required; sources: none)

## Exposure / Open Position Rules

- Position note: Maximum planned holding period is five trading days.
- Position note: Position size must be smaller than the equivalent unlevered exposure.
- [ ] P1: Limit planned holding period to five trading days. (exposure: time-boxed tactical; tags: path-dependency, volatility; sources: [S1], [S2])
- [ ] P2: Cap notional exposure before order entry. (exposure: reduced notional; tags: sizing, leverage; sources: [S1])
- [ ] C1: Record entry price, stop, target, and expiry date before trade. (open)
- [ ] C2: Confirm no earnings, CPI, FOMC, or other event invalidates sizing. (open)
- [ ] C3: Review realized leverage and tracking after each close. (open)

## Evidence / Stale-Source Summary

- Tracked Items: 10
- Supported Items: 9
- Unsupported Items: 1
- Sources: 2
- Unused Sources: 0
- Stale Sources: 0
- No stale sources detected.
- Unsupported catalyst CAT1

## Questions before action

- [ ] Q1: Does the latest review decision still support the contemplated action?
- [ ] Q2: Are all high-severity risks understood with current mitigation evidence?
- [ ] Q3: Have open catalysts been checked for new source-backed status changes?
- [ ] Q4: Do open position rules permit the proposed exposure?
- [ ] Q5: Are stale, unused, or unsupported evidence gaps acceptable before action?
- [ ] Q6: What evidence would falsify the action after execution?

## Sources

- [S1] Leveraged and inverse ETF risk bulletin. Investor Education Desk, 2026-03-15. https://example.com/leveraged-etf-risk-bulletin
- [S2] Volatility drag illustration. Portfolio Research Notes, 2026-04-05. https://example.com/volatility-drag
