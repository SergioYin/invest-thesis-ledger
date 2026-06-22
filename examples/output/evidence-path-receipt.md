# Evidence Path Walkthrough Receipt

> This is a research organization tool, not investment advice.

- Workflow: bounded evidence path walkthrough receipt
- Tool version: 1.9.3
- Deterministic: yes
- Zero dependencies: yes
- Fixture source: checked-in demo ledgers

## Reviewer Path

### ledger_fixtures

- Action: start from checked-in thesis ledgers
- Paths: `examples/oklo-ai-power.json`, `examples/leveraged-etf-discipline.json`

### quickstart_receipt

- Action: confirm fixture, review packet, queue, dashboard, hash, and boundary receipt
- Paths: `examples/output/quickstart-receipt.md`, `examples/output/quickstart-receipt.json`

### decision_review_walkthrough

- Action: follow validation, evidence, review packet, and review queue reproduction steps
- Paths: `examples/output/decision-review-walkthrough.md`, `examples/output/decision-review-walkthrough.json`

### review_artifacts

- Action: inspect evidence, decision review pack, and review queue artifacts
- Paths: `examples/output/oklo-ai-power-evidence.md`, `examples/output/oklo-ai-power-decision-review-pack.md`, `examples/output/review-queue.md`

### dashboard_artifacts

- Action: open static no-JS dashboard index and manifest
- Paths: `examples/output/html-dashboard/index.html`, `examples/output/html-dashboard/manifest.json`

## Fixture Inputs

- `examples/oklo-ai-power.json` (5035 bytes; sha256 `e275acdb478565eb9c5a91d8b1fe7309f308d6b112fadab25c26596308da2cb6`)
- `examples/leveraged-etf-discipline.json` (3926 bytes; sha256 `b538a1256b9c824eb18b9b1f954008472faa88f7116bbe54c2831c499a37a9af`)

## Linked Receipts

- `examples/output/quickstart-receipt.md`
- `examples/output/quickstart-receipt.json`
- `examples/output/decision-review-walkthrough.md`
- `examples/output/decision-review-walkthrough.json`

## Generated Artifact Hashes

| Path | Kind | Bytes | SHA-256 | Checked-In Match |
| --- | --- | ---: | --- | --- |
| `examples/output/decision-review-walkthrough.json` | walkthrough | 3661 | `5d6f47b21bb97154db9a78b1e3394ff485d28a7d58abcd5ef1a1376145a30595` | yes |
| `examples/output/decision-review-walkthrough.md` | walkthrough | 2917 | `f3353da1449797e37a9107f62eceaa117ff8e56a8a6f05093eda91898259e96b` | yes |
| `examples/output/html-dashboard/action-plan.html` | dashboard | 6807 | `bc8693d4c6498785687731ee4d4dc95251ac2f4acb6babec0e991691544da8f3` | yes |
| `examples/output/html-dashboard/evidence-audit.html` | dashboard | 2820 | `768b6f9c2acd6960d3aebe02aeeafb5171c00d97db9f403a36181a0a85a91112` | yes |
| `examples/output/html-dashboard/index.html` | dashboard | 1518 | `9e72bf48eece5b7bba3bd87015ba17ead2bc4e0b2c61dcac7f3e1f41a61bdf3b` | yes |
| `examples/output/html-dashboard/leveraged-etf-discipline.html` | dashboard | 5569 | `1017429f90e6b3f6b4a536384f0b7b07cf5cc982dc533442f53e57c7d694dc3f` | yes |
| `examples/output/html-dashboard/manifest.json` | dashboard | 346 | `0eb2b65f94d30dd3b51d2625586ef04dcebc0b7a4a9dc7f3c9820ab237af4522` | yes |
| `examples/output/html-dashboard/oklo-ai-power.html` | dashboard | 5849 | `48ed09388ee7ddf657b8e6c350fc99a5ac59fa76ddc8f02cca2127569fdce981` | yes |
| `examples/output/html-dashboard/portfolio.html` | dashboard | 3494 | `5cc3a89b7bc828b8df61d9e749ab7ac4342552ee3b16514e043243bd8d119c9b` | yes |
| `examples/output/html-dashboard/style.css` | dashboard | 1505 | `9782f8bde5983d76c244fd01925accb96a45adeb6c2cbc86e14c5ddc2eb2e160` | yes |
| `examples/output/html-dashboard/watchlist.html` | dashboard | 1702 | `ec6c9ba615eb172eec5993323d3ce295d78bf59ec7d009af3c0ef3514a5e346a` | yes |
| `examples/output/oklo-ai-power-decision-review-pack.json` | review | 9644 | `f149c8c448277707ac701bdbc491ba00b50327612f7ce683232079c470cdc5be` | yes |
| `examples/output/oklo-ai-power-decision-review-pack.md` | review | 4595 | `d5b46e7440c9cdffc147c38856abdfcc7c51a5d439938780165cb48583c2044b` | yes |
| `examples/output/oklo-ai-power-evidence.json` | evidence | 1802 | `e575628051e014edcaf385ff350e15d9b3edeb1ed55ad4b56afc8671b924e9a9` | yes |
| `examples/output/oklo-ai-power-evidence.md` | evidence | 1024 | `e8addaa37f0c5a7ec8d5ba0a303a472fcd9e9eff6206fbf040ae00ce2fa32d5d` | yes |
| `examples/output/quickstart-receipt.json` | receipt | 5091 | `fbc42b0811b5dac44d5e28536c5fa83e8cd08289c0194b66d76c49c0aaca9e0f` | yes |
| `examples/output/quickstart-receipt.md` | receipt | 3880 | `3c39b79ffc30c74631f0939aa2b723e7df78e2504b980d50b16f1522a9572d95` | yes |
| `examples/output/review-queue.json` | review | 2819 | `c169814cb727b00e45854609b5f983530c151a0a81f53bf2ef99feccac0bdf7d` | yes |
| `examples/output/review-queue.md` | review | 1473 | `52f3c159dad1dfbafc5f5e281c93ea9a5f429370f69688c846f8b5b4a9fa7e1b` | yes |

## Hygiene Checks

- public_fixture_hygiene: pass
- not_investment_advice_notice: pass
- advice_wording: pass
- portable_paths: pass
- secret_terms: pass

## Boundaries

- No live market data: yes
- No broker connection: yes
- No account data: yes
- No orders: yes
- No trading execution: yes
- Not investment advice: yes

This evidence path receipt connects only checked-in fixture ledgers, deterministic generated receipts, local review/dashboard artifacts, and SHA-256 hashes. It does not fetch live market data, connect to broker or account systems, place orders, execute trades, or provide investment advice.
