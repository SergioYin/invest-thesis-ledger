# Package Readiness Receipt

> This is a research organization tool, not investment advice.

- Workflow: package publish landing readiness receipt
- Tool version: 1.9.3
- Deterministic: yes
- Zero dependencies: yes

## Package Metadata

- Name: invest-thesis-ledger
- Version: 1.9.3
- Requires Python: >=3.9

## Public CLI Entry Points

- `invest-thesis-ledger` -> `invest_thesis_ledger.cli:main`

## Public Artifact Evidence

| Path | Kind | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `README.md` | docs | 25686 | `8c25d95f8b163bdbc4306023d69b9e991da1e5b4134282e1afb10c422efe836b` |
| `CHANGELOG.md` | docs | 16364 | `9ee52c3e582eed94c76dcbaa0bd453e1e436e0c68063e880bbdc2d2544303e87` |
| `docs/ledger-schema.md` | docs | 29010 | `b8627bd4bb70c9dbef6e29d8dec52390a76c99cc22d7af190e6e62d6f54fc078` |
| `pyproject.toml` | package-metadata | 920 | `3491f0659b321750839bfde83df22c24128536e99a532cf1e3356223bd60b3dd` |
| `examples/oklo-ai-power.json` | fixture-input | 5035 | `e275acdb478565eb9c5a91d8b1fe7309f308d6b112fadab25c26596308da2cb6` |
| `examples/leveraged-etf-discipline.json` | fixture-input | 3926 | `b538a1256b9c824eb18b9b1f954008472faa88f7116bbe54c2831c499a37a9af` |
| `examples/output/oklo-ai-power-decision-review-pack.md` | demo-output | 4595 | `d5b46e7440c9cdffc147c38856abdfcc7c51a5d439938780165cb48583c2044b` |
| `examples/output/oklo-ai-power-decision-review-pack.json` | demo-output | 9644 | `f149c8c448277707ac701bdbc491ba00b50327612f7ce683232079c470cdc5be` |
| `examples/output/quickstart-receipt.md` | demo-output | 3880 | `3c39b79ffc30c74631f0939aa2b723e7df78e2504b980d50b16f1522a9572d95` |
| `examples/output/quickstart-receipt.json` | demo-output | 5091 | `fbc42b0811b5dac44d5e28536c5fa83e8cd08289c0194b66d76c49c0aaca9e0f` |
| `examples/output/evidence-path-receipt.md` | demo-output | 5265 | `e55f7c8c6740eef18c2afca38b1ab120090436b45b6e138f20e9e8ff4e9f6e7b` |
| `examples/output/evidence-path-receipt.json` | demo-output | 9553 | `7830629279eb9666335832f258b0c1f14f0fc56da12f198b8b1ccfe35bf1a844` |
| `examples/output/visual-walkthrough/README.md` | demo-output | 3409 | `31048d5fbd9f08f50775bdb330c4f760fecf08f400da99f5ceae0ce56bae4a4d` |
| `examples/output/visual-walkthrough/visual-walkthrough.json` | demo-output | 4080 | `6b5fee76dc1247c38ec6d9e5a972c22a4c5b4fc735ae8b07b2f46ce235fd4b60` |

## Verification Commands

- `python -m invest_thesis_ledger --version`
- `python -m invest_thesis_ledger package-readiness-receipt --output examples/output/package-readiness-receipt.md --json-output examples/output/package-readiness-receipt.json`
- `python scripts/selfcheck.py`
- `python -m unittest discover -s tests`

## Release and Landing Readiness Notes

- Package metadata name and version are present in pyproject.toml.
- Console script entry points are public and deterministic.
- README, schema docs, changelog, and demo receipt artifacts are checked in.
- Examples are local fixtures and generated static artifacts only.
- No timestamp, wall-clock, live market data, broker, order, private path, or credential material is included.

## Hygiene Checks

- public_fixture_hygiene: pass
- portable_paths: pass
- secret_terms: pass

## Finance Safety Boundaries

- Local/static source files only: yes
- No live data: yes
- No broker: yes
- No orders: yes
- No personalized investment advice/recommendations: yes
- No private data: yes

This package readiness receipt inspects local/static checked-in source files and public demo artifacts only. It does not fetch live data, connect to brokers, place orders, produce personalized investment advice or recommendations, or read private data.
