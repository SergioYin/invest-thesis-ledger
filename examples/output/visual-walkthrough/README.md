# Visual Walkthrough Screenshot Guide

> This is a research organization tool, not investment advice.

- Workflow: bounded visual walkthrough screenshot guide
- Tool version: 1.9.2
- Deterministic: yes
- Zero dependencies: yes
- Fixture source: checked-in demo ledgers
- Visual format: local SVG screenshot guide

## Route

### dashboard_review

- View: Open the static no-JS dashboard index and inspect the local review queue.
- Local artifact: `examples/output/html-dashboard/index.html`
- Command: `python -m invest_thesis_ledger html-dashboard examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output-dir examples/output/html-dashboard`
- Visual asset: `dashboard-route.svg`

### decision_review_pack

- View: Open the Oklo decision review pack and review evidence, risks, catalysts, and questions.
- Local artifact: `examples/output/oklo-ai-power-decision-review-pack.md`
- Command: `python -m invest_thesis_ledger decision-review-pack examples/oklo-ai-power.json --output examples/output/oklo-ai-power-decision-review-pack.md --json-output examples/output/oklo-ai-power-decision-review-pack.json`
- Visual asset: `decision-review-pack-route.svg`

### evidence_path_receipt

- View: Open the evidence path receipt and confirm linked receipts, hashes, and boundaries.
- Local artifact: `examples/output/evidence-path-receipt.md`
- Command: `python -m invest_thesis_ledger evidence-path-receipt --output examples/output/evidence-path-receipt.md --json-output examples/output/evidence-path-receipt.json`
- Visual asset: `evidence-path-route.svg`

## Fixture Inputs

- `examples/oklo-ai-power.json` (5035 bytes; sha256 `e275acdb478565eb9c5a91d8b1fe7309f308d6b112fadab25c26596308da2cb6`)
- `examples/leveraged-etf-discipline.json` (3926 bytes; sha256 `b538a1256b9c824eb18b9b1f954008472faa88f7116bbe54c2831c499a37a9af`)

## Linked Local Artifacts

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `examples/output/html-dashboard/index.html` | 1518 | `208168a583d53779dc377ec1923d590499c9483d361f28312d1d3ad7857b1ce2` |
| `examples/output/oklo-ai-power-decision-review-pack.md` | 4595 | `d5b46e7440c9cdffc147c38856abdfcc7c51a5d439938780165cb48583c2044b` |
| `examples/output/evidence-path-receipt.md` | 5265 | `44dad31cc9792f8fef5eb08281130e9741921d87ca38da962d4743b7781682a4` |
| `examples/output/evidence-path-receipt.json` | 9553 | `a665fa568382f4103e9faa239ff8053d970245e7e2cbc5a494e9b15a6eb94365` |

## Visual Assets

| Path | Kind | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `dashboard-route.svg` | svg-screenshot-guide | 1939 | `5ad7ec98b8e01bce937438d80fd6ac795b0e38da9e8b55ec9d1300385eaedae8` |
| `decision-review-pack-route.svg` | svg-screenshot-guide | 2065 | `3cc734ff2be6fc27e173d117f560a19594e1d2f38c041148ba15a58fcfc58db1` |
| `evidence-path-route.svg` | svg-screenshot-guide | 1961 | `333054792785b58d010871d76bef305debfff6b2cfe90ead4ff7b509b5029e5b` |

## Hygiene Checks

- portable_paths: pass
- secret_terms: pass

## Boundaries

- No live market data: yes
- No broker connection: yes
- No account data: yes
- No orders: yes
- No trading execution: yes
- Not investment advice: yes

This visual walkthrough is a deterministic screenshot guide generated from checked-in fixture labels and local artifact paths only. It does not capture live websites, fetch market data, connect to broker or account systems, place orders, execute trades, or provide investment advice.
