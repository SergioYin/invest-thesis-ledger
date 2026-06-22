# Cold-Reviewer Quickstart Receipt

> This is a research organization tool, not investment advice.

- Workflow: cold-reviewer quickstart receipt
- Tool version: 1.9.3
- Deterministic: yes
- Zero dependencies: yes

## Exact Quickstart Commands

- `python -m invest_thesis_ledger validate examples/oklo-ai-power.json`
- `python -m invest_thesis_ledger decision-review-pack examples/oklo-ai-power.json --output examples/output/oklo-ai-power-decision-review-pack.md --json-output examples/output/oklo-ai-power-decision-review-pack.json`
- `python -m invest_thesis_ledger review-queue examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output examples/output/review-queue.md --json-output examples/output/review-queue.json`
- `python -m invest_thesis_ledger html-dashboard examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output-dir examples/output/html-dashboard`
- `python -m invest_thesis_ledger quickstart-receipt --output examples/output/quickstart-receipt.md --json-output examples/output/quickstart-receipt.json`

## Static Fixture Inputs

- `examples/oklo-ai-power.json` (5035 bytes; sha256 `e275acdb478565eb9c5a91d8b1fe7309f308d6b112fadab25c26596308da2cb6`)
- `examples/leveraged-etf-discipline.json` (3926 bytes; sha256 `b538a1256b9c824eb18b9b1f954008472faa88f7116bbe54c2831c499a37a9af`)

## Generated Dashboard and Review Outputs

| Path | Kind | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `examples/output/html-dashboard/action-plan.html` | dashboard | 6807 | `bc8693d4c6498785687731ee4d4dc95251ac2f4acb6babec0e991691544da8f3` |
| `examples/output/html-dashboard/evidence-audit.html` | dashboard | 2820 | `768b6f9c2acd6960d3aebe02aeeafb5171c00d97db9f403a36181a0a85a91112` |
| `examples/output/html-dashboard/index.html` | dashboard | 1518 | `9e72bf48eece5b7bba3bd87015ba17ead2bc4e0b2c61dcac7f3e1f41a61bdf3b` |
| `examples/output/html-dashboard/leveraged-etf-discipline.html` | dashboard | 5569 | `1017429f90e6b3f6b4a536384f0b7b07cf5cc982dc533442f53e57c7d694dc3f` |
| `examples/output/html-dashboard/manifest.json` | dashboard | 346 | `0eb2b65f94d30dd3b51d2625586ef04dcebc0b7a4a9dc7f3c9820ab237af4522` |
| `examples/output/html-dashboard/oklo-ai-power.html` | dashboard | 5849 | `48ed09388ee7ddf657b8e6c350fc99a5ac59fa76ddc8f02cca2127569fdce981` |
| `examples/output/html-dashboard/portfolio.html` | dashboard | 3494 | `5cc3a89b7bc828b8df61d9e749ab7ac4342552ee3b16514e043243bd8d119c9b` |
| `examples/output/html-dashboard/style.css` | dashboard | 1505 | `9782f8bde5983d76c244fd01925accb96a45adeb6c2cbc86e14c5ddc2eb2e160` |
| `examples/output/html-dashboard/watchlist.html` | dashboard | 1702 | `ec6c9ba615eb172eec5993323d3ce295d78bf59ec7d009af3c0ef3514a5e346a` |
| `examples/output/oklo-ai-power-decision-review-pack.json` | review | 9644 | `f149c8c448277707ac701bdbc491ba00b50327612f7ce683232079c470cdc5be` |
| `examples/output/oklo-ai-power-decision-review-pack.md` | review | 4595 | `d5b46e7440c9cdffc147c38856abdfcc7c51a5d439938780165cb48583c2044b` |
| `examples/output/review-queue.json` | review | 2819 | `c169814cb727b00e45854609b5f983530c151a0a81f53bf2ef99feccac0bdf7d` |
| `examples/output/review-queue.md` | review | 1473 | `52f3c159dad1dfbafc5f5e281c93ea9a5f429370f69688c846f8b5b4a9fa7e1b` |

## Hygiene Checks

- public_fixture_hygiene: pass
- stale_review_date: pass
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

This receipt is for deterministic research organization only. It uses checked-in fixture ledgers and generated local artifacts, does not fetch live market data, does not connect to broker or account systems, does not place orders or execute trades, and is not investment advice.
