# Changelog

## 1.6.1 - 2026-05-12

- Hardened `verify-archive` to reject symlink generated or hash-listed files before hashing file bytes.
- Added manifest/archive-summary consistency checks for ledger IDs and tool versions, archive ledger counts, and duplicate generated file entries.
- Kept `diff-archive` on the verifier path and report metadata from verified archive metadata.
- Updated package/schema version, README, schema docs, tests, selfcheck, and checked-in fixtures for v1.6.1.

## 1.6.0 - 2026-05-12

- Added `diff-archive` command for deterministic Markdown and JSON diffs between two verified portable research archives.
- Reused archive verification before diffing, with exit code 1 for invalid archives and 2 for unreadable or malformed archive inputs.
- Compared manifest generated files, archive-summary SHA-256 hashes, ledger IDs, tool versions, and file counts with added, removed, changed, and unchanged file counts.
- Updated package/schema version, README, schema docs, tests, selfcheck, and checked-in fixtures for v1.6.0.

## 1.5.0 - 2026-05-12

- Added `verify-archive` command for deterministic portable archive verification.
- Verified archive manifests, summaries, generated file presence, local relative paths, SHA-256 hashes, self-hash exclusion, and absence of workflow or dependency files.
- Added explicit verifier exit codes: 0 for valid archives, 1 for content validation failures, and 2 for unreadable or malformed archive inputs.
- Updated package/schema version, README, schema docs, tests, selfcheck, and checked-in fixtures for v1.5.0.

## 1.4.0 - 2026-05-12

- Added `archive` command for deterministic portable research archives across two or more ledgers.
- Added archive output with `README.md`, normalized per-ledger JSON copies, per-ledger brief/risk/history/decision/scenario Markdown, aggregate portfolio/evidence-audit/watchlist/action-plan Markdown, `manifest.json`, and `archive-summary.json`.
- Added SHA-256 file hashes in the archive summary using the Python standard library, with no timestamps, absolute paths, workflow files, dependency files, or external data.
- Kept archive writes validation-first and cleanly staged so existing output directories are replaced only after all ledgers validate and archive files are generated.
- Updated package/schema version, README, schema docs, tests, selfcheck, and checked-in fixtures for v1.4.0.

## 1.3.0 - 2026-05-12

- Expanded `demo-bundle` output with `evidence-audit.md` and `action-plan.md`.
- Expanded `html-dashboard` output with `evidence-audit.html` and `action-plan.html`.
- Reused existing evidence audit and action plan payloads for aggregate static pages without adding JavaScript, external assets, workflow files, market data, or personal advice wording.
- Kept bundle and dashboard manifests deterministic with local generated file links only.
- Updated package/schema version, README, schema docs, tests, selfcheck, and checked-in fixtures for v1.3.0.

## 1.2.0 - 2026-05-12

- Added `action-plan` command for weekly action plans across two or more ledgers.
- Added deterministic Markdown/JSON output with ranked actions, `TBD` owner placeholders, cadence labels, reason codes, blockers, source-quality warnings, and per-ledger next checklists.
- Composed the action plan from existing review queue, watchlist, evidence audit, risk, exposure, and catalyst payloads without market data.
- Ranked tied duplicate thesis IDs/tickers by the normalized action payload and kept unsupported/unused source-quality records as warnings rather than blockers.
- Kept generated language educational and not investment advice, avoiding personal trading instructions.
- Added checked-in action plan example outputs generated from the Oklo and leveraged ETF examples.
- Updated package/schema version, README, schema docs, tests, selfcheck, and checked-in fixtures for v1.2.0.

## 1.1.0 - 2026-05-12

- Added `evidence-audit` command for portfolio-level evidence quality audits across two or more ledgers.
- Added Markdown/JSON audit output for field-level coverage, unsupported items, unused sources, stale sources, duplicate source URLs across ledgers, and deterministic per-ledger evidence quality rankings.
- Included checklist items in the portfolio evidence audit when present while reusing the existing evidence and stale-source logic.
- Added checked-in evidence audit example outputs generated from the Oklo and leveraged ETF examples.
- Updated package/schema version, README, schema docs, tests, selfcheck, and checked-in fixtures for v1.1.0.

## 1.0.0 - 2026-05-12

- Added `html-dashboard` command for static deterministic no-JS HTML dashboards across two or more ledgers.
- Added HTML output with `index.html`, `style.css`, one per-ledger page, `portfolio.html`, `watchlist.html`, and timestamp-free `manifest.json`.
- Reused existing brief, risk, history, decision memo, scenario plan, portfolio, and watchlist payloads for dashboard content.
- Escaped generated HTML with the Python standard library only; no external CSS, JavaScript, images, or fonts are used.
- Updated package/schema version, README, schema docs, tests, selfcheck, and checked-in example fixtures for v1.0.0.

## 0.9.0 - 2026-05-12

- Added `demo-bundle` command for static deterministic Markdown bundles across two or more ledgers.
- Added bundle output with `index.md`, per-ledger brief/risk/history/decision memo/scenario plan reports, portfolio summary, watchlist, and timestamp-free `manifest.json`.
- Added clean output-directory overwrite behavior after successful validation of all input ledgers.
- Added checked-in demo bundle example outputs generated from the Oklo and leveraged ETF examples.
- Updated README, schema docs, tests, and selfcheck for demo bundle coverage.

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
