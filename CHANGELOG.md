# Changelog

## 0.8.0 - 2026-05-12

- Added `watchlist` command for weekly human review lists across two or more ledgers.
- Added deterministic watchlist Markdown/JSON output ranked by review queue score with ticker, title, priority, next action, nearest open catalyst, latest review date/decision, stale source count, high-risk count, and open position-rule count.
- Hardened watchlist ranking for duplicate thesis IDs, tied queue rows, same-day review ties, and same-date catalyst ties.
- Added checked-in watchlist example outputs generated from the Oklo and leveraged ETF examples.
- Updated README, schema docs, tests, and selfcheck for watchlist coverage.

## 0.7.0 - 2026-05-12

- Added `scenario-plan` command for deterministic base/bull/bear scenario planning from one ledger.
- Added structured scenario-plan JSON and Markdown output covering assumptions inferred from confidence, catalyst triggers, risk mitigation actions, position-rule constraints, and evidence gaps.
- Added checked-in Oklo scenario plan example outputs.
- Updated README, schema docs, tests, and selfcheck for scenario plan coverage.

## 0.6.0 - 2026-05-12

- Added `decision-memo` command for deterministic pre-trade/review memos from one ledger.
- Added structured decision memo JSON and Markdown output covering asset/thesis snapshot, latest review, broker view summary, high risks, catalyst checklist, exposure/open position rules, evidence/stale-source summary, and questions before action.
- Added checked-in Oklo decision memo example outputs.
- Updated README, schema docs, tests, and selfcheck for decision memo coverage.

## 0.5.0 - 2026-05-12

- Added `review-queue` command for prioritizing two or more ledgers for human review.
- Added deterministic Markdown/JSON review queue outputs with per-ledger scores, priority labels, reasons, and next action text.
- Added checked-in review queue example outputs generated from the Oklo and leveraged ETF examples.
- Updated README, schema docs, tests, and selfcheck for review queue coverage.

## 0.4.0 - 2026-05-12

- Added `portfolio` command for deterministic aggregation across two or more ledgers.
- Added portfolio Markdown/JSON outputs for assets, thesis count, risk severity counts, risk tag counts, catalyst status/window/date lists, broker rating counts, review decisions, and stale source warnings.
- Added checked-in portfolio example outputs generated from the Oklo and leveraged ETF examples.
- Updated README, schema docs, tests, and selfcheck for portfolio coverage.

## 0.3.0 - 2026-05-12

- Added `broker-matrix` command for broker, desk, or institution rating/target/thesis matrices.
- Added `exposure` command for mapping risk tags and position rules into exposure checklists.
- Added `init-template` command for deterministic starter ledger generation.
- Expanded optional schema support for `broker_views`, `position_rules`, and risk `tags`.
- Updated examples, demo fixtures, tests, schema docs, README, and selfcheck for the v0.3.0 finance workflow expansion.

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
