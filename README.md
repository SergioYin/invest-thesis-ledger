# invest-thesis-ledger

A zero-dependency Python package and CLI for maintaining investment thesis
ledgers as JSON, then rendering deterministic briefs, risk reports, review
timelines, thesis drift comparisons, catalyst calendars, evidence coverage
reports, broker/institution matrices, exposure checklists, deterministic
starter ledger generation, decision memos, scenario plans, portfolio-level
summaries, and review queues. v0.7.0 adds the scenario plan workflow while
preserving compatibility with v0.1.0 through v0.6.0 ledgers.

This project is for research organization only. It is not investment advice.

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

Render a deterministic base/bull/bear scenario plan:

```bash
python -m invest_thesis_ledger scenario-plan examples/oklo-ai-power.json --output scenario-plan.md --json-output scenario-plan.json
```

Aggregate two or more ledgers into a portfolio summary:

```bash
python -m invest_thesis_ledger portfolio examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output portfolio.md --json-output portfolio.json
```

Prioritize two or more ledgers for human review:

```bash
python -m invest_thesis_ledger review-queue examples/oklo-ai-power.json examples/leveraged-etf-discipline.json --output review-queue.md --json-output review-queue.json
```

Create a deterministic starter ledger:

```bash
python -m invest_thesis_ledger init-template --asset MSFT --name "Microsoft Corporation" --type equity --output ledger.json
```

The starter includes one placeholder source, assumption, risk, and review so it
validates immediately and shows the expected source-linking pattern.

All generated outputs are deterministic for the same input file or ordered
input file list.

## Ledger Format

Ledgers are JSON objects. The v0.7.0 required fields are:

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

The formal v0.7.0 schema reference is in `docs/ledger-schema.md`.

See:

- `examples/oklo-ai-power.json`
- `examples/oklo-ai-power-prior.json`
- `examples/leveraged-etf-discipline.json`

## Demo Outputs

Checked-in deterministic CLI output fixtures are available under
`examples/output/`:

- `examples/output/oklo-ai-power-brief.md`
- `examples/output/oklo-ai-power-risk.md`
- `examples/output/oklo-ai-power-risk.json`
- `examples/output/oklo-ai-power-history.md`
- `examples/output/oklo-ai-power-history.json`
- `examples/output/oklo-ai-power-calendar.md`
- `examples/output/oklo-ai-power-calendar.json`
- `examples/output/oklo-ai-power-evidence.md`
- `examples/output/oklo-ai-power-evidence.json`
- `examples/output/oklo-ai-power-broker.md`
- `examples/output/oklo-ai-power-broker.json`
- `examples/output/oklo-ai-power-exposure.md`
- `examples/output/oklo-ai-power-exposure.json`
- `examples/output/oklo-ai-power-decision-memo.md`
- `examples/output/oklo-ai-power-decision-memo.json`
- `examples/output/oklo-ai-power-scenario-plan.md`
- `examples/output/oklo-ai-power-scenario-plan.json`
- `examples/output/oklo-ai-power-drift.md`
- `examples/output/oklo-ai-power-drift.json`
- `examples/output/portfolio-summary.md`
- `examples/output/portfolio-summary.json`
- `examples/output/review-queue.md`
- `examples/output/review-queue.json`

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

`decision-memo` uses the same normalized broker, catalyst, exposure, and
evidence payloads to produce a deterministic pre-trade/review memo with the
latest review, high-risk list, open position rules, stale-source summary, and
questions to answer before action.

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
