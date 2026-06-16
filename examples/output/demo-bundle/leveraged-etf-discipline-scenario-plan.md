# Scenario Plan: Leveraged ETF Discipline Ledger

> This is a research organization tool, not investment advice.

## Asset / Thesis

- Ledger ID: leveraged-etf-discipline
- Updated: 2026-05-19
- Asset: LEV2X (Generic 2x Equity Index ETF)
- Type: fund
- Thesis: Leveraged ETFs can express short-term tactical views, but path dependency, volatility drag, and position sizing rules must dominate the decision process.

## Plan Summary

- Cases: 3
- Open Scenario Triggers: 2
- Open Position Constraints: 2
- Risk Mitigation Actions: 2
- Evidence Gaps: 1

## Base Case

Current thesis remains intact if source-backed assumptions hold and open risks stay controlled.

### Assumptions

- A1: The instrument is used for a defined short-term thesis rather than a long-term allocation. (confidence: high; sources: [S1])
- A2: Volatility conditions are reviewed before entry and daily while open. (confidence: medium; sources: [S2])

### Risk Conditions

- R1: Volatility drag (severity: high; probability: high)
- R2: Oversized exposure (severity: high; probability: medium)

### Catalyst Triggers

- CAT2: Macro event calendar supports a time-boxed tactical setup. (date: 2026-06-10) (direction: base; status: required; sources: [S1])
- CAT1: Index breaks above predefined technical level. (window: before entry) (direction: base; status: required; sources: none)

### Risk Mitigation Actions

- R1: Use only with explicit holding-period limit and daily review. (risk: Volatility drag)
- R2: Cap notional exposure before order entry. (risk: Oversized exposure)

### Position-Rule Constraints

- [ ] P1: Limit planned holding period to five trading days. (exposure: time-boxed tactical; tags: path-dependency, volatility; sources: [S1], [S2])
- [ ] P2: Cap notional exposure before order entry. (exposure: reduced notional; tags: sizing, leverage; sources: [S1])

### Evidence Gaps

- UNSUPPORTED-catalyst-CAT1: Add source support for catalyst CAT1.

## Bull Case

Upside case requires higher-conviction assumptions and positive catalysts becoming source-backed.

### Assumptions

- A1: The instrument is used for a defined short-term thesis rather than a long-term allocation. (confidence: high; sources: [S1])
- A2: Volatility conditions are reviewed before entry and daily while open. (confidence: medium; sources: [S2])

### Risk Conditions

- No risks mapped to this case.

### Catalyst Triggers

- No open catalyst triggers mapped to this case.

### Risk Mitigation Actions

- R1: Use only with explicit holding-period limit and daily review. (risk: Volatility drag)
- R2: Cap notional exposure before order entry. (risk: Oversized exposure)

### Position-Rule Constraints

- [ ] P1: Limit planned holding period to five trading days. (exposure: time-boxed tactical; tags: path-dependency, volatility; sources: [S1], [S2])
- [ ] P2: Cap notional exposure before order entry. (exposure: reduced notional; tags: sizing, leverage; sources: [S1])

### Evidence Gaps

- UNSUPPORTED-catalyst-CAT1: Add source support for catalyst CAT1.

## Bear Case

Downside case is driven by low-confidence assumptions, severe risks, or unresolved evidence gaps.

### Assumptions

- No assumptions mapped to this case.

### Risk Conditions

- R1: Volatility drag (severity: high; probability: high)
- R2: Oversized exposure (severity: high; probability: medium)

### Catalyst Triggers

- No open catalyst triggers mapped to this case.

### Risk Mitigation Actions

- R1: Use only with explicit holding-period limit and daily review. (risk: Volatility drag)
- R2: Cap notional exposure before order entry. (risk: Oversized exposure)

### Position-Rule Constraints

- [ ] P1: Limit planned holding period to five trading days. (exposure: time-boxed tactical; tags: path-dependency, volatility; sources: [S1], [S2])
- [ ] P2: Cap notional exposure before order entry. (exposure: reduced notional; tags: sizing, leverage; sources: [S1])

### Evidence Gaps

- UNSUPPORTED-catalyst-CAT1: Add source support for catalyst CAT1.

## Sources

- [S1] Leveraged and inverse ETF risk bulletin. Investor Education Desk, 2026-03-15. https://example.com/leveraged-etf-risk-bulletin
- [S2] Volatility drag illustration. Portfolio Research Notes, 2026-04-05. https://example.com/volatility-drag
