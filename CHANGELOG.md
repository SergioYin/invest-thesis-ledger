# Changelog

## 0.2.0 - 2026-05-12

- Added `compare` command for deterministic thesis, assumption, risk, and review drift reports.
- Added `calendar` command for dated and windowed catalyst tracking.
- Added `evidence` command for source coverage, unused-source reporting, and stale-source warnings.
- Expanded catalyst schema to support object entries with `date`, `window`, `status`, and `source_ids`.
- Updated examples, demo fixtures, tests, schema docs, and selfcheck for the expanded finance workflow.

## 0.1.0 - 2026-05-12

- Added zero-dependency Python package `invest_thesis_ledger`.
- Added CLI commands: `validate`, `brief`, `risk`, and `history`.
- Added deterministic Markdown and JSON renderers.
- Added example ledgers for Oklo AI power demand and leveraged ETF discipline.
- Added stdlib tests and `scripts/selfcheck.py`.
