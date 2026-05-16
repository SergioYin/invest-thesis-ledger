# Optional Decision Review Pack Integration Notes

These examples show how a `decision-review-pack` can consume or complement
outputs from adjacent tools without adding runtime dependencies, import
requirements, or private context.

The CLI does not read these files automatically. Treat them as generic
companion artifacts that a reviewer can use to update ordinary ledger fields:
`sources`, `risks`, `position_rules`, `checklist`, `catalysts`, and `reviews`.
After those fields are updated, `decision-review-pack` will include the new
evidence through the existing ledger schema.

## Portfolio Risk Compass

[portfolio-risk-compass-summary.json](portfolio-risk-compass-summary.json) is a
generic portfolio-level risk snapshot. To use it with a ledger:

- add the snapshot as a normal source if it is approved for the ledger;
- convert relevant concentration, correlation, liquidity, or exposure findings
  into source-backed risks, checklist items, or position rules;
- record a review note if the portfolio context changes the thesis status.

The decision review pack then complements the portfolio snapshot by explaining
which per-ledger assumptions, risks, catalysts, and source gaps drive the next
review.

## Leveraged ETP Risk Lab

[leveraged-etp-risk-lab-summary.json](leveraged-etp-risk-lab-summary.json) is a
generic daily-reset/path-dependence risk snapshot for leveraged ETP review. To
use it with a ledger:

- add the lab output as a source if it is approved for the ledger;
- convert path-dependence, rebalance, compounding, liquidity, and holding-period
  findings into risks, position rules, or checklist items;
- preserve any unresolved findings as open checklist items instead of treating
  the lab output as an automated decision.

The decision review pack then gives a reviewer the evidence map, high-risk
summary, open position discipline, and exact reproduction command for the
ledger-native packet.

## Generated Packet Links

The checked-in review packet examples generated from ordinary ledger fields are:

- [Oklo decision review pack Markdown](../output/oklo-ai-power-decision-review-pack.md)
- [Oklo decision review pack JSON](../output/oklo-ai-power-decision-review-pack.json)
- [Demo bundle index with per-ledger packets](../output/demo-bundle/index.md)
- [Portable archive README with per-ledger packets](../output/archive/README.md)

These files are generated artifacts, not imported companion data. Regenerate
them with `decision-review-pack`, `demo-bundle`, or `archive` after approved
companion findings have been translated into ledger fields.

## Boundary

- No brokerage, market-data, or external-service integration is implied.
- No JSON schema extension is required.
- No dependency on `portfolio-risk-compass` or `leveraged-etp-risk-lab` is
  required.
- The examples are research organization artifacts only, not investment advice.
- The examples do not provide market data, personalized recommendations, or
  buy/sell/hold instructions.
