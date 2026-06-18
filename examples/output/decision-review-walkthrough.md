# Decision Review Walkthrough

> This is a research organization tool, not investment advice.

- Workflow: bounded decision review walkthrough
- Tool version: 1.9.2
- Deterministic: yes
- Zero dependencies: yes
- Fixture source: checked-in demo ledgers

## Exact Rerun Commands

- `python -m invest_thesis_ledger validate examples/oklo-ai-power.json`
- `python -m invest_thesis_ledger evidence examples/oklo-ai-power.json --output examples/output/oklo-ai-power-evidence.md --json-output examples/output/oklo-ai-power-evidence.json`
- `python -m invest_thesis_ledger decision-review-pack examples/oklo-ai-power.json --output examples/output/oklo-ai-power-decision-review-pack.md --json-output examples/output/oklo-ai-power-decision-review-pack.json`
- `python -m invest_thesis_ledger review-queue examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output examples/output/review-queue.md --json-output examples/output/review-queue.json`
- `python -m invest_thesis_ledger decision-review-walkthrough --output examples/output/decision-review-walkthrough.md --json-output examples/output/decision-review-walkthrough.json`

## Fixture Inputs

- `examples/oklo-ai-power.json` (5035 bytes; sha256 `e275acdb478565eb9c5a91d8b1fe7309f308d6b112fadab25c26596308da2cb6`)
- `examples/leveraged-etf-discipline.json` (3926 bytes; sha256 `b538a1256b9c824eb18b9b1f954008472faa88f7116bbe54c2831c499a37a9af`)

## Generated Review and Evidence Artifacts

| Path | Kind | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `examples/output/oklo-ai-power-decision-review-pack.json` | review | 9644 | `f149c8c448277707ac701bdbc491ba00b50327612f7ce683232079c470cdc5be` |
| `examples/output/oklo-ai-power-decision-review-pack.md` | review | 4595 | `d5b46e7440c9cdffc147c38856abdfcc7c51a5d439938780165cb48583c2044b` |
| `examples/output/oklo-ai-power-evidence.json` | evidence | 1802 | `e575628051e014edcaf385ff350e15d9b3edeb1ed55ad4b56afc8671b924e9a9` |
| `examples/output/oklo-ai-power-evidence.md` | evidence | 1024 | `e8addaa37f0c5a7ec8d5ba0a303a472fcd9e9eff6206fbf040ae00ce2fa32d5d` |
| `examples/output/review-queue.json` | review | 2819 | `c169814cb727b00e45854609b5f983530c151a0a81f53bf2ef99feccac0bdf7d` |
| `examples/output/review-queue.md` | review | 1473 | `52f3c159dad1dfbafc5f5e281c93ea9a5f429370f69688c846f8b5b4a9fa7e1b` |

## Stale-Date Hygiene

- Status: pass

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

This walkthrough uses checked-in demo ledger fixtures and deterministic local renderers only. It does not fetch live market data, does not connect to broker or account systems, does not place orders, and is not investment advice.
