# invest-thesis-ledger

A zero-dependency Python package and CLI for maintaining investment thesis
ledgers as JSON, then rendering deterministic briefs, risk reports, review
timelines, thesis drift comparisons, catalyst calendars, evidence coverage
reports, broker/institution matrices, exposure checklists, deterministic
starter ledger generation, decision-review packs, decision memos, scenario
plans, portfolio-level summaries, portfolio evidence audits, review queues,
weekly watchlists, weekly action plans, static demo bundles, portable research
archives, archive verification, archive diffs, and no-JS HTML dashboards.
v1.8.0 adds review-ready decision-review packets while preserving concise
exit-code-2 reporting and compatibility with v0.1.0 through v1.7.4 ledgers.
Optional public integration notes show how decision-review packs can use
portfolio-risk-compass and leveraged-etp-risk-lab outputs through
ordinary ledger fields, without adding dependencies.
For the public decision-review-pack walkthrough, start with
[examples/integration/README.md](examples/integration/README.md).

This project is for research organization only. It is not investment advice,
does not provide market data, and does not recommend buying, selling, or
holding any asset. Review outputs are structured notes for independent human
review.

## Agent skill

This repository includes a generic agent-facing skill protocol at:

```text
skills/agent/invest-thesis-ledger/SKILL.md
```

Use it to teach compatible agents when and how to call this CLI for investment thesis ledgers, risk reports, decision memos, scenario plans, portfolio reviews, archives, and HTML dashboards. The skill is intentionally separate from the README: the README explains the tool to humans, while the skill is an executable protocol for agents.

## Install

Run directly from a checkout:

```bash
python -m invest_thesis_ledger --version
```

Install locally:

```bash
python -m pip install .
invest-thesis-ledger --version
```

No runtime dependencies are required.

## Cold-User Quickstart

From a fresh checkout, run the checked-in example through validation and the
review packet renderer:

```bash
python -m invest_thesis_ledger validate examples/oklo-ai-power.json
python -m invest_thesis_ledger decision-review-pack examples/oklo-ai-power.json --output /tmp/oklo-review-pack.md --json-output /tmp/oklo-review-pack.json
```

Open `/tmp/oklo-review-pack.md` first. It is the reviewer-facing packet with
the thesis status, deterministic review score, evidence map, stale-source
warnings, high risks, open catalysts, next review questions, exact reproduction
command, and a non-advice/no-market-data boundary. Open
`/tmp/oklo-review-pack.json` when you need the same packet as structured data.

Checked-in equivalents are available at
[examples/output/oklo-ai-power-decision-review-pack.md](examples/output/oklo-ai-power-decision-review-pack.md)
and
[examples/output/oklo-ai-power-decision-review-pack.json](examples/output/oklo-ai-power-decision-review-pack.json).
For multi-ledger review, start with the generated demo bundle index at
[examples/output/demo-bundle/index.md](examples/output/demo-bundle/index.md) or
the portable archive index at
[examples/output/archive/README.md](examples/output/archive/README.md).

## Commands

Validate a ledger:

```bash
python -m invest_thesis_ledger validate examples/oklo-ai-power.json
```

Output:

```text
ledger: oklo-ai-power
title: Oklo AI Power Demand Thesis
sources: 3
assumptions: 2
risks: 2
reviews: 2
status: valid
```

Render a source-attributed brief:

```bash
python -m invest_thesis_ledger brief examples/oklo-ai-power.json --output brief.md
```

Render a risk report with Markdown and JSON outputs:

```bash
python -m invest_thesis_ledger risk examples/oklo-ai-power.json --output risk.md --json-output risk.json
```

Render a review timeline and thesis drift report:

```bash
python -m invest_thesis_ledger history examples/oklo-ai-power.json --output history.md --json-output history.json
```

Compare two ledger snapshots for thesis, assumption, risk, and review drift:

```bash
python -m invest_thesis_ledger compare examples/oklo-ai-power-prior.json examples/oklo-ai-power.json --output drift.md --json-output drift.json
```

Render a catalyst calendar with optional catalyst `date` and `window` fields:

```bash
python -m invest_thesis_ledger calendar examples/oklo-ai-power.json --output calendar.md --json-output calendar.json
```

Render source coverage and deterministic stale-source warnings:

```bash
python -m invest_thesis_ledger evidence examples/oklo-ai-power.json --output evidence.md --json-output evidence.json
```

Render a broker/institution rating, target, and thesis matrix:

```bash
python -m invest_thesis_ledger broker-matrix examples/oklo-ai-power.json --output broker.md --json-output broker.json
```

Render an exposure checklist from `position_rules` and risk `tags`:

```bash
python -m invest_thesis_ledger exposure examples/oklo-ai-power.json --output exposure.md --json-output exposure.json
```

Render a pre-trade/review decision memo:

```bash
python -m invest_thesis_ledger decision-memo examples/oklo-ai-power.json --output decision-memo.md --json-output decision-memo.json
```

Render a review-ready decision review pack. The packet is for research
organization and independent review only; it contains no market data and no
buy/sell/hold recommendation:

```bash
python -m invest_thesis_ledger decision-review-pack examples/oklo-ai-power.json --output decision-review-pack.md --json-output decision-review-pack.json
```

Render a deterministic base/bull/bear scenario plan:

```bash
python -m invest_thesis_ledger scenario-plan examples/oklo-ai-power.json --output scenario-plan.md --json-output scenario-plan.json
```

Aggregate two or more ledgers into a portfolio summary:

```bash
python -m invest_thesis_ledger portfolio examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output portfolio.md --json-output portfolio.json
```

Audit portfolio evidence quality across two or more ledgers:

```bash
python -m invest_thesis_ledger evidence-audit examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output audit.md --json-output audit.json
```

Prioritize two or more ledgers for human review:

```bash
python -m invest_thesis_ledger review-queue examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output review-queue.md --json-output review-queue.json
```

Render a weekly watchlist ranked by review queue score:

```bash
python -m invest_thesis_ledger watchlist examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output watchlist.md --json-output watchlist.json
```

Render a weekly action plan from review queue, watchlist, evidence audit, risk,
exposure, and catalyst payloads:

```bash
python -m invest_thesis_ledger action-plan examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output action-plan.md --json-output action-plan.json
```

Write a static deterministic Markdown demo bundle:

```bash
python -m invest_thesis_ledger demo-bundle examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output-dir demo-bundle
```

Write a deterministic portable research archive with source ledgers, rendered
reports, manifest, README index, and SHA-256 summary:

```bash
python -m invest_thesis_ledger archive examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output-dir research-archive
```

Verify a portable research archive:

```bash
python -m invest_thesis_ledger verify-archive research-archive
```

Compare two verified portable research archives:

```bash
python -m invest_thesis_ledger diff-archive old-archive new-archive --output archive-diff.md --json-output archive-diff.json
```

Write a static deterministic no-JS HTML dashboard:

```bash
python -m invest_thesis_ledger html-dashboard examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output-dir html-dashboard
```

Create a deterministic starter ledger:

```bash
python -m invest_thesis_ledger init-template --asset MSFT --name "Microsoft Corporation" --type equity --output ledger.json
```

The starter includes one placeholder source, assumption, risk, and review so it
validates immediately and shows the expected source-linking pattern.

All generated outputs are deterministic for the same input file or ordered
input file list.
Commands that write paired Markdown and JSON outputs stage both files before
committing either final path. If a paired write fails, the command exits 2 with
concise stderr and does not leave a newly written companion output behind.

## Ledger Format

Ledgers are JSON objects. The v1.8.0 required fields are:

- `ledger_version`
- `thesis_id`
- `title`
- `asset` with `name`, `type`, and `ticker`
- `created`
- `updated`
- `thesis`
- `sources`
- `assumptions`
- `risks`
- `reviews`

Optional fields currently rendered by the CLI:

- `positions`
- `catalysts`
- `broker_views`
- `position_rules`
- `checklist`

`catalysts` may be strings or objects. Object catalysts can include `id`,
`title`, `date`, `window`, `status`, and `source_ids`; catalyst `source_ids`
must reference known sources and must not repeat the same source within one
catalyst. `calendar` sorts dated catalysts first and keeps undated window-based
catalysts deterministic.

`broker_views` entries are objects for institution, rating, target, as-of date,
short thesis, and `source_ids`. `broker-matrix` sorts views by institution and
ID.

`position_rules` entries may be strings or objects. Object rules can include
`id`, `rule`, `status`, `exposure`, `tags`, and `source_ids`. Risks may include
optional string `tags`; `exposure` combines these risk tags with position rules
into a checklist.

The formal v1.8.0 schema reference is in `docs/ledger-schema.md`.

See:

- [examples/oklo-ai-power.json](examples/oklo-ai-power.json)
- [examples/oklo-ai-power-prior.json](examples/oklo-ai-power-prior.json)
- [examples/leveraged-etf-discipline.json](examples/leveraged-etf-discipline.json)
- [examples/integration/README.md](examples/integration/README.md)

## Demo Outputs

Checked-in deterministic CLI output fixtures are available under
`examples/output/`. Start with these generated artifact links:

- [decision review pack Markdown](examples/output/oklo-ai-power-decision-review-pack.md)
- [decision review pack JSON](examples/output/oklo-ai-power-decision-review-pack.json)
- [demo bundle index](examples/output/demo-bundle/index.md)
- [demo bundle manifest](examples/output/demo-bundle/manifest.json)
- [portable archive README](examples/output/archive/README.md)
- [portable archive manifest](examples/output/archive/manifest.json)
- [portable archive SHA-256 summary](examples/output/archive/archive-summary.json)
- [HTML dashboard index](examples/output/html-dashboard/index.html)
- [HTML dashboard manifest](examples/output/html-dashboard/manifest.json)

Additional single-command fixtures include brief, risk, history, calendar,
evidence, broker matrix, exposure, decision memo, scenario plan, drift,
portfolio summary, evidence audit, review queue, watchlist, and action plan
Markdown/JSON outputs:

- [examples/output/](examples/output/)
- per-ledger demo bundle artifacts for brief, risk, history, decision review
  pack, decision memo, and scenario plan reports
- per-ledger archive JSON copies and brief, risk, history, decision review
  pack, decision, and scenario reports
- per-ledger HTML dashboard pages

## Development

Run the full stdlib selfcheck:

```bash
python scripts/selfcheck.py
```

Run tests directly:

```bash
python -m unittest discover -s tests
```

If `pytest` is available, the tests are also compatible with:

```bash
pytest
```

## Notes

`evidence` treats a source as stale when its `date` is more than 180 days older
than the ledger `updated` date. Sources are not compared to the current
wall-clock date, so stale-source warnings stay deterministic and independent of
the day the command is run.

`review-queue` uses the same deterministic stale-source logic and scores each
ledger from stale sources, high-severity risks, upcoming/open catalysts, stale
reviews, open checklist items, and open position rules. Stale sources are 2
points each, high/critical/severe risks are 3 points each, upcoming or open
catalysts are 1 point each, stale reviews are 3 points, open checklist items
are 1 point each, and open position rules are 1 point each. Scores of 8 or more
are high priority, scores of 4 to 7 are medium priority, and lower scores are
low priority.

`watchlist` reuses review queue scoring to rank the weekly review list, then
adds the fields needed for a human scan: ticker, title, priority, next action,
nearest open catalyst, latest review date and decision, stale source count,
high-risk count, and open position-rule count. Ranking remains deterministic
when ledgers have duplicate `thesis_id` values or tied scores; watchlist rows
are derived from each ledger directly and ties include latest-review and nearest
open-catalyst details.

`evidence-audit` validates all input ledgers before writing anything, then
aggregates source coverage across assumptions, risks, reviews, catalysts,
broker views, position rules, and checklist items. It reports unsupported
items, unused sources, stale sources using the same ledger `updated` logic as
`evidence`, duplicate source URLs that appear in more than one ledger, and a
deterministic per-ledger evidence quality score ranked from highest to lowest.

`action-plan` validates all input ledgers before writing anything, then ranks
weekly research actions by cadence, review score, priority, lower source
quality score, stable ledger fields, and the normalized action payload. Stale
sources are source-quality blockers; unsupported and unused source records are
warnings for review.

`demo-bundle` validates all input ledgers before writing anything, then cleanly
overwrites the target output directory with static Markdown files: `index.md`,
per-ledger brief/risk/history/decision review pack/decision memo/scenario plan reports,
`portfolio-summary.md`, `evidence-audit.md`, `watchlist.md`, `action-plan.md`,
and `manifest.json`. The manifest lists generated files, tool version, and
input ledger IDs only; it intentionally contains no timestamps.

`archive` validates all input ledgers before writing anything, then cleanly
overwrites the target output directory with a portable research archive:
`README.md`, `manifest.json`, `archive-summary.json`, deterministic per-ledger
JSON copies, per-ledger brief/risk/history/decision review pack/decision/scenario reports,
`portfolio.md`, `evidence-audit.md`, `watchlist.md`, and `action-plan.md`.
The summary records counts and SHA-256 file hashes using relative filenames
only. `archive-summary.json` is listed in `generated_files` but excluded from
`file_hashes` so the summary does not need to hash its own bytes. Archive
metadata contains no timestamps or absolute paths. `verify-archive` reads
`manifest.json` and `archive-summary.json`, verifies generated file presence,
relative archive-local paths, SHA-256 hashes, manifest/summary metadata
consistency, archive counts, self-hash exclusion, and the absence of symlink,
workflow, or dependency files. It exits 0 for a valid archive, 1 for content
validation failures, and 2 for unreadable or malformed archive inputs.
`diff-archive` first applies the same verification semantics to both archives;
it exits 2 for unreadable or malformed archive inputs and exits 1 with
deterministic validation errors for invalid archives. When both archives are
valid, it writes Markdown and JSON with added, removed, changed, and unchanged
file information plus old/new ledger IDs, tool versions, file counts, and
changed/unchanged status.

`html-dashboard` validates all input ledgers before writing anything, then
cleanly overwrites the target output directory with static HTML/CSS files:
`index.html`, `style.css`, one page per ledger, `portfolio.html`,
`evidence-audit.html`, `watchlist.html`, `action-plan.html`, and
`manifest.json`. It uses the existing brief, risk, history, decision memo,
scenario plan, portfolio, evidence audit, watchlist, and action plan payloads;
all HTML is escaped with the Python standard library, with no external CSS,
JavaScript, images, or fonts.

`decision-memo` uses the same normalized broker, catalyst, exposure, and
evidence payloads to produce a deterministic pre-trade/review memo with the
latest review, high-risk list, open position rules, stale-source summary, and
questions to answer before action.

`decision-review-pack` uses existing ledger/demo data to produce Markdown and
JSON packets for independent review. Each packet includes thesis status, review
score and drivers, latest review, a review evidence map, deterministic evidence
freshness, high risks, open catalysts, next review questions, sources, exact
command provenance using stable artifact filenames, and an explicit non-advice
boundary. It contains no market data, does not provide personalized advice, and
does not recommend buying, selling, or holding. A cold-user example is checked
in as
[examples/output/oklo-ai-power-decision-review-pack.md](examples/output/oklo-ai-power-decision-review-pack.md)
with structured output at
[examples/output/oklo-ai-power-decision-review-pack.json](examples/output/oklo-ai-power-decision-review-pack.json).

Optional companion artifacts from tools such as `portfolio-risk-compass` or
`leveraged-etp-risk-lab` can be used without any CLI dependency by translating
approved findings into normal ledger `sources`, `risks`, `position_rules`,
`checklist`, `catalysts`, or `reviews`. The packet will then use those
fields through the existing schema. If the external artifact should remain
separate, keep it beside the packet as portfolio or instrument-specific context;
the generated packet remains ledger-native and reproducible. See
`examples/integration/` for generic public examples.

`scenario-plan` uses only existing ledger fields to derive base, bull, and bear
cases from assumption confidence, risk severity/probability, open catalyst
triggers, mitigation text, position-rule constraints, and evidence gaps.
Assumptions with high/strong/confirmed/validated confidence map to base and
bull cases, medium/moderate assumptions map to base and bull cases,
watch/watchlist/neutral or unrecognized confidence maps to base, and
low/weak/unproven/unknown confidence maps to bear. Catalyst trigger direction is
inferred with whole-word terms: positive terms map to bull, negative terms map to
bear, and unmatched triggers map to base. Evidence gaps are ordered as
low-confidence assumptions, stale sources, unused sources, then unsupported
items.

## License

MIT. See `LICENSE`.
