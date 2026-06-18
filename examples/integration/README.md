# Optional Decision Review Pack Integration Notes

These examples show how a `decision-review-pack` can consume or complement
outputs from adjacent tools without adding runtime dependencies, import
requirements, or private context.

The CLI does not read these files automatically. Treat them as generic
companion artifacts that a reviewer can use to update ordinary ledger fields:
`sources`, `risks`, `position_rules`, `checklist`, `catalysts`, and `reviews`.
After those fields are updated, `decision-review-pack` will include the new
evidence through the existing ledger schema.

## Decision Review Pack Walkthrough

Start with the checked-in public example ledger and validate it:

```bash
python -m invest_thesis_ledger validate examples/oklo-ai-power.json
```

Render the single-ledger review packet to temporary paths:

```bash
python -m invest_thesis_ledger decision-review-pack examples/oklo-ai-power.json --output /tmp/oklo-review-pack.md --json-output /tmp/oklo-review-pack.json
```

Artifacts:

- `/tmp/oklo-review-pack.md`: reviewer-facing Markdown packet
- `/tmp/oklo-review-pack.json`: structured packet payload
- [checked-in Markdown fixture](../output/oklo-ai-power-decision-review-pack.md)
- [checked-in JSON fixture](../output/oklo-ai-power-decision-review-pack.json)

Render the checked-in public walkthrough when you need one artifact that shows
validation, evidence output, review packet output, review queue output, fixture
hashes, generated artifact hashes, stale-date hygiene, public hygiene checks,
and explicit non-advice/no-live-data/no-broker boundaries:

```bash
python -m invest_thesis_ledger decision-review-walkthrough --output /tmp/decision-review-walkthrough.md --json-output /tmp/decision-review-walkthrough.json
```

Checked-in equivalents are
[examples/output/decision-review-walkthrough.md](../output/decision-review-walkthrough.md)
and
[examples/output/decision-review-walkthrough.json](../output/decision-review-walkthrough.json).

Render the bounded evidence path receipt when a reviewer needs the fixture,
quickstart receipt, walkthrough, review/dashboard artifact, hash, and boundary
trail in one place:

```bash
python -m invest_thesis_ledger evidence-path-receipt --output /tmp/evidence-path-receipt.md --json-output /tmp/evidence-path-receipt.json
```

Checked-in equivalents are
[examples/output/evidence-path-receipt.md](../output/evidence-path-receipt.md)
and
[examples/output/evidence-path-receipt.json](../output/evidence-path-receipt.json).

Render the local visual screenshot guide when a reviewer needs a deterministic
SVG route through the dashboard, decision review pack, and evidence path
receipt:

```bash
python -m invest_thesis_ledger visual-walkthrough --output-dir /tmp/visual-walkthrough
```

The checked-in equivalent is
[examples/output/visual-walkthrough/README.md](../output/visual-walkthrough/README.md)
with structured output at
[examples/output/visual-walkthrough/visual-walkthrough.json](../output/visual-walkthrough/visual-walkthrough.json).

For a public multi-ledger demo bundle:

```bash
python -m invest_thesis_ledger demo-bundle examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output-dir /tmp/invest-thesis-demo-bundle
```

Review `/tmp/invest-thesis-demo-bundle/index.md` first. The checked-in
equivalent is [examples/output/demo-bundle/index.md](../output/demo-bundle/index.md),
with per-ledger packet files listed in the bundle manifest.

For a portable archive with verification metadata:

```bash
python -m invest_thesis_ledger archive examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output-dir /tmp/invest-thesis-archive
python -m invest_thesis_ledger verify-archive /tmp/invest-thesis-archive
```

Review `/tmp/invest-thesis-archive/README.md`,
`/tmp/invest-thesis-archive/manifest.json`, and
`/tmp/invest-thesis-archive/archive-summary.json`. Checked-in equivalents are
[examples/output/archive/README.md](../output/archive/README.md),
[examples/output/archive/manifest.json](../output/archive/manifest.json), and
[examples/output/archive/archive-summary.json](../output/archive/archive-summary.json).

These outputs are deterministic research organization artifacts. They use
ledger fields and generated file metadata only; they do not add market data,
private paths, secrets, or buy/sell/hold recommendations.

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
- [Decision review walkthrough Markdown](../output/decision-review-walkthrough.md)
- [Decision review walkthrough JSON](../output/decision-review-walkthrough.json)
- [Evidence path receipt Markdown](../output/evidence-path-receipt.md)
- [Evidence path receipt JSON](../output/evidence-path-receipt.json)
- [Visual walkthrough guide](../output/visual-walkthrough/README.md)
- [Visual walkthrough JSON](../output/visual-walkthrough/visual-walkthrough.json)
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
