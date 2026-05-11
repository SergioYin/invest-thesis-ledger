# Ledger Schema v1.6.0

This document defines the JSON ledger format accepted by `invest-thesis-ledger`
v1.6.0. Ledgers are research organization records only and are not investment
advice.

## Document Shape

A ledger is a single JSON object. The CLI validates required fields, required
nested object fields, duplicate IDs, source references, and a few basic type
constraints. Unknown fields are allowed so teams can keep local annotations
without breaking the renderer.

## Required Top-Level Fields

| Field | Type | Description |
| --- | --- | --- |
| `ledger_version` | string | Schema version. v1.6.0 ledgers should use `"1.6.0"`. v0.1.0 through v1.5.0 remain accepted for compatibility; other values validate with a warning. |
| `thesis_id` | string | Stable machine-readable ledger identifier. |
| `title` | string | Human-readable thesis title. |
| `asset` | object | Asset metadata. |
| `created` | string | Creation date, recommended as `YYYY-MM-DD`. |
| `updated` | string | Last material update date, recommended as `YYYY-MM-DD`. |
| `thesis` | string | Current thesis statement. |
| `sources` | array | Source objects used by assumptions, risks, and reviews. |
| `assumptions` | array | Assumption objects supporting the thesis. |
| `risks` | array | Risk objects for the thesis. |
| `reviews` | array | Dated thesis review objects. |

## Asset

`asset` is required and must contain:

| Field | Type | Description |
| --- | --- | --- |
| `name` | string | Asset or issuer name. |
| `type` | string | Asset class or instrument type, such as `equity`, `fund`, or `crypto`. |
| `ticker` | string | Ticker, symbol, or short asset code. |

## Sources

Each entry in `sources` must contain:

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique source identifier, such as `S1`. |
| `title` | string | Source title. |
| `publisher` | string | Publisher, authoring organization, or internal desk. |
| `date` | string | Source date, recommended as `YYYY-MM-DD`. |
| `url` | string | URL or durable reference location. |

Source IDs must be unique. Rendered source lists are sorted by source ID for
deterministic output.

## Assumptions

Each entry in `assumptions` must contain:

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique assumption identifier, such as `A1`. |
| `statement` | string | The assumption being tracked. |
| `confidence` | string | Current confidence label. |
| `source_ids` | array | Source IDs supporting the assumption. |

Every `source_ids` entry must be a string that references an existing source,
and duplicate source references within one item are invalid.

## Risks

Each entry in `risks` must contain:

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique risk identifier, such as `R1`. |
| `name` | string | Short risk name. |
| `severity` | string | Severity label. |
| `probability` | string | Probability label. |
| `mitigation` | string | Mitigation or discipline rule. |
| `source_ids` | array | Source IDs supporting the risk. |

Every `source_ids` entry must be a string that references an existing source,
and duplicate source references within one item are invalid.

Optional risk field:

| Field | Type | Description |
| --- | --- | --- |
| `tags` | array | String risk tags such as `valuation`, `regulatory`, `liquidity`, or `leverage`. |

## Reviews

Each entry in `reviews` must contain:

| Field | Type | Description |
| --- | --- | --- |
| `date` | string | Review date, recommended as `YYYY-MM-DD`. |
| `decision` | string | Review decision, such as `watch`, `hold`, `exit`, or `policy`. |
| `summary` | string | Review summary. |
| `source_ids` | array | Source IDs supporting the review. |

Optional review field:

| Field | Type | Description |
| --- | --- | --- |
| `drift` | string | Notes on thesis drift since the prior review. |

Reviews may be stored in any order. Validation warns when they are not sorted by
date, while history output sorts reviews by date.

## Optional Rendered Fields

The CLI renders these optional top-level fields when present:

| Field | Type | Rendered By | Description |
| --- | --- | --- | --- |
| `positions` | array | `brief`, `decision-memo` | Position notes or sizing discipline. |
| `catalysts` | array | `brief`, `calendar`, `decision-memo`, `evidence`, `scenario-plan` | Catalysts or evidence that could change conviction. |
| `broker_views` | array | `broker-matrix`, `decision-memo`, `evidence` | Broker, desk, or institution rating/target/thesis views. |
| `position_rules` | array | `decision-memo`, `exposure`, `evidence`, `scenario-plan` | Position sizing, exposure, and trade discipline rules. |
| `checklist` | array | `decision-memo`, `risk` | Risk checklist items. |

`catalysts` entries may be strings or objects. String entries are accepted for
v0.1.0 compatibility and render as undated watch items. Object entries can
include:

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Catalyst identifier. Defaults to `CAT<n>` if omitted. |
| `title` | string | Catalyst title or event description. |
| `date` | string | Optional specific catalyst date, recommended as `YYYY-MM-DD`. |
| `window` | string | Optional timing window when a precise date is not useful. |
| `status` | string | Optional status label. Defaults to `watch`. |
| `source_ids` | array | Optional source IDs supporting the catalyst. |

Every catalyst `source_ids` entry must be a string that references an existing
source, and duplicate source references within one catalyst are invalid.
`calendar` output sorts catalysts with explicit dates first by date, then
undated catalysts by window and ID.

`broker_views` entries must be objects. They can include:

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Broker view identifier. Defaults to `B<n>` if omitted. |
| `institution` | string | Broker, bank, research desk, or internal institution name. |
| `rating` | string | Rating or stance label. |
| `target` | string | Price target, scenario target, or target discipline. |
| `as_of` | string | View date, recommended as `YYYY-MM-DD`. |
| `thesis` | string | Short institution thesis or rationale. |
| `source_ids` | array | Optional source IDs supporting the view. |

Every broker view `source_ids` entry must be a string that references an
existing source, and duplicate source references within one view are invalid.
`broker-matrix` output sorts views by institution name and ID.

`position_rules` entries may be strings or objects. String entries are accepted
as open rules with no tags or sources. Object entries can include:

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Position rule identifier. Defaults to `P<n>` if omitted. |
| `rule` | string | Rule text. `item` or `description` are accepted as fallbacks by renderers. |
| `status` | string | Status label. `done`, `closed`, `passed`, and `complete` render as checked. |
| `exposure` | string | Exposure bucket or sizing note. |
| `tags` | array | String tags that map the rule to risk categories. |
| `source_ids` | array | Optional source IDs supporting the rule. |

Every position rule `source_ids` entry must be a string that references an
existing source, and duplicate source references within one rule are invalid.

`checklist` entries may be strings or objects. Object entries can include:

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Checklist identifier. Defaults to `C<n>` if omitted. |
| `item` | string | Checklist text. |
| `status` | string | Status label. `done`, `closed`, `passed`, and `complete` render as checked. |
| `source_ids` | array | Optional source IDs supporting the checklist item. |

Every checklist `source_ids` entry must be a string that references an existing
source, and duplicate source references within one item are invalid.

## Determinism

For the same input file or ordered input file list, v1.6.0 CLI outputs are
deterministic:

- JSON outputs are serialized with sorted keys and two-space indentation.
- History reviews are sorted by review date.
- Calendar catalysts are sorted by date presence, date, window, and ID.
- Broker views are sorted by institution and ID.
- Position rules are sorted by ID, and exposure risk tags are sorted by tag.
- Portfolio assets are sorted by ticker and ledger ID.
- Portfolio catalyst and stale-source lists are sorted by stable ledger and
  item fields.
- Review queue and watchlist items are sorted by descending score, priority,
  ticker, ledger ID, and title.
- Action plan items are sorted by cadence, descending review score, priority,
  lower source quality score, stable asset/ledger fields, and finally the
  normalized action payload so duplicate thesis IDs and tickers do not fall
  back to input order.
- Review queue reasons are sorted by the scoring categories documented below;
  reason item IDs use the stable order for their source report, risk,
  checklist, or position-rule type.
- Decision memos reuse the deterministic broker, catalyst, exposure, evidence,
  and history payload ordering.
- Scenario plans sort assumptions, risks, position constraints, mitigation
  actions, triggers, and evidence gaps by stable IDs or existing normalized
  report ordering.
- Demo bundle manifests list generated files, tool version, and input ledger
  IDs without timestamps or wall-clock data.
- Portable archive manifests and summaries list generated files, tool version,
  input ledger IDs, counts, and SHA-256 file hashes without timestamps,
  wall-clock data, or absolute paths.
- HTML dashboard manifests list generated files, tool version, and input ledger
  IDs without timestamps or wall-clock data.
- HTML dashboard pages escape all HTML with the Python standard library and do
  not include external CSS, JavaScript, images, or fonts.
- Evidence stale-source warnings are measured against ledger `updated`, not the
  current wall-clock date.
- Source reference lists preserve the ledger order inside each item.
- Rendered source sections are sorted by source ID.
- `init-template` uses fixed placeholder dates so repeated runs with the same
  arguments produce byte-identical JSON.

## v1.6.0 Reports

`compare <old.json> <new.json> --output drift.md --json-output drift.json`
loads and validates both ledgers, then compares:

- `thesis`
- `assumptions`, keyed by `id`
- `risks`, keyed by `id`
- `reviews`, keyed by `id` when present or deterministic `REV<n>:<date>`
  fallback IDs when omitted

The JSON output contains `added`, `removed`, `changed`, and `unchanged` groups
for assumptions, risks, and reviews.

`calendar <ledger.json> --output calendar.md --json-output calendar.json`
normalizes catalyst strings and objects into deterministic catalyst records with
`id`, `title`, `date`, `window`, `status`, and `source_ids`.

`evidence <ledger.json> --output evidence.md --json-output evidence.json`
reports source coverage for assumptions, risks, reviews, catalysts, broker
views, and position rules. It also reports unused sources and stale sources. A
source is stale when its `date` is more than 180 days older than ledger
`updated`.

`broker-matrix <ledger.json> --output broker.md --json-output broker.json`
normalizes optional `broker_views` into a matrix of institution, rating, target,
as-of date, thesis, and sources. The JSON output also includes rating counts.

`exposure <ledger.json> --output exposure.md --json-output exposure.json`
maps optional risk `tags` and `position_rules` into an exposure checklist. The
JSON output includes tag counts, normalized risks, normalized position rules,
and combined checklist entries.

`decision-memo <ledger.json> --output decision-memo.md --json-output decision-memo.json`
loads and validates one ledger, then renders a deterministic pre-trade/review
memo containing:

- asset and thesis snapshot
- assumptions and latest dated review
- broker view summary and normalized broker views
- high/critical/severe risks
- catalyst checklist
- position notes, open position rules, and open checklist items
- evidence coverage, stale sources, unused sources, and unsupported items
- final questions before action

`scenario-plan <ledger.json> --output scenario-plan.md --json-output scenario-plan.json`
loads and validates one ledger, then renders deterministic base, bull, and bear
scenario cases from existing ledger fields. No new schema fields are required.
The structured JSON and Markdown include:

- base/bull/bear cases inferred from assumption confidence and risk
  severity/probability
- open catalyst triggers with deterministic whole-word case direction inference:
  positive terms map to bull, negative terms map to bear, and unmatched triggers
  map to base
- risk mitigation actions from each risk's `mitigation` field
- open position-rule constraints from normalized `position_rules`
- evidence gaps from low-confidence assumptions, stale sources, unused sources,
  and unsupported evidence items

Assumption confidence maps deterministically: high/strong/confirmed/validated
and medium/moderate assumptions appear in base and bull cases,
watch/watchlist/neutral or unrecognized confidence appears in base, and
low/weak/unproven/unknown confidence appears in bear. Risk conditions are
included in the base case, low/minor risk conditions are included in bull, and
medium/moderate/high/critical/severe risk conditions are included in bear.
Evidence gaps are ordered by review priority: low-confidence assumptions, stale
sources, unused sources, then unsupported evidence items.

`init-template --asset TICKER --name NAME --type TYPE --output ledger.json`
writes a deterministic starter ledger with v1.6.0 fields, fixed placeholder
dates, one source-backed assumption, one risk, one review, and a thesis ID
derived from the ticker.

```bash
portfolio <ledger-a.json> <ledger-b.json> [...] --output portfolio.md --json-output portfolio.json
```

The `portfolio` command loads and validates every input ledger before writing
output. It requires at least two ledgers and aggregates:

- assets and thesis count
- risk severity counts
- risk tag counts
- catalyst status counts, window counts, and dated/windowed catalyst list
- broker rating counts by institution and rating
- review decision counts
- stale source warnings using the same deterministic ledger-updated-date logic
  as `evidence`

```bash
evidence-audit <ledger-a.json> <ledger-b.json> [...] --output audit.md --json-output audit.json
```

The `evidence-audit` command loads and validates every input ledger before
writing output. It requires at least two ledgers and aggregates portfolio
evidence quality across:

- assumptions
- risks
- reviews
- catalysts
- broker views
- position rules
- checklist items, when the field exists

The JSON and Markdown outputs include portfolio totals, field-level coverage,
unsupported items, unused sources, stale sources using the same deterministic
ledger `updated` stale-source logic as `evidence`, duplicate source URLs that
appear in more than one ledger, and per-ledger evidence quality scores. Scores
are deterministic integers from 0 to 100: up to 60 points from item support, 20
points from source utilization, and 20 points from source freshness. Ledgers are
ranked by highest score first, then by unsupported, unused, and stale counts,
then stable asset and ledger labels.

```bash
review-queue <ledger-a.json> <ledger-b.json> [...] --output review-queue.md --json-output review-queue.json
```

The `review-queue` command loads and validates every input ledger before
writing output. It requires at least two ledgers and prioritizes human review
using a deterministic score:

- stale sources: 2 points each
- high, critical, or severe risks: 3 points each
- upcoming or open catalysts: 1 point each
- stale review, when the latest review date is before `ledger.updated`: 3
  points
- open checklist items: 1 point each
- open position rules: 1 point each

Scores of 8 or more are `high` priority, scores of 4 to 7 are `medium`
priority, and lower scores are `low` priority. The JSON output includes
per-ledger reason records with reason type, count, score contribution, item IDs,
and next action text.

```bash
watchlist <ledger-a.json> <ledger-b.json> [...] --output watchlist.md --json-output watchlist.json
```

The `watchlist` command loads and validates every input ledger before writing
output. It requires at least two ledgers and reuses review queue scoring to rank
the weekly human review list. Duplicate `thesis_id` values are allowed in the
input set; ranking and per-ledger watchlist details are derived from each ledger
directly, rather than by matching rows back by thesis ID. Tied rows are ordered
deterministically by score, priority, ticker, thesis ID, title, latest review,
nearest open catalyst, counts, and next action. The Markdown and JSON outputs
include:

- rank and review queue score
- ticker and title
- priority and next action
- nearest open catalyst
- latest review date and decision
- stale source count
- high/critical/severe risk count
- open position-rule count

The nearest open catalyst is the earliest unresolved catalyst on or after
`ledger.updated`, or an undated open catalyst when no dated candidate sorts
earlier. Exact ties are broken by date presence, date, window, ID, title, and
status. The latest review is selected by date, then decision, summary, and
source IDs so same-day review ties do not depend on input order.

```bash
action-plan <ledger-a.json> <ledger-b.json> [...] --output action-plan.md --json-output action-plan.json
```

The `action-plan` command loads and validates every input ledger before writing
output. It requires at least two ledgers and creates an educational weekly
workflow without market data. The plan composes existing normalized payloads:

- review queue scores, priorities, reasons, and next action text
- watchlist nearest open catalyst, latest review, and weekly counts
- evidence audit coverage and per-ledger source quality score
- risk high-severity records and checklist status
- exposure open position rules and tag counts
- catalyst open status records

The Markdown and JSON outputs include ranked actions with a `TBD` owner
placeholder, cadence labels (`now`, `this-week`, or `watch`), reason codes,
blockers, source-quality warnings, and per-ledger next checklists. Stale sources
are source-quality blockers; unsupported and unused source records remain
warnings for review. The rendered language is for research organization only
and is not investment advice.

```bash
demo-bundle <ledger-a.json> <ledger-b.json> [...] --output-dir demo-bundle
```

The `demo-bundle` command loads and validates every input ledger before writing
output. It requires at least two ledgers and cleanly overwrites the output
directory with a static Markdown bundle:

- `index.md`
- one brief, risk report, history report, decision memo, and scenario plan per
  input ledger
- `portfolio-summary.md`
- `evidence-audit.md`
- `watchlist.md`
- `action-plan.md`
- `manifest.json`

The manifest is deterministic and contains only `generated_files`,
`ledger_ids`, and `tool_version`. It does not include timestamps.

```bash
archive <ledger-a.json> <ledger-b.json> [...] --output-dir research-archive
```

The `archive` command loads and validates every input ledger before writing
output. It requires at least two ledgers and cleanly overwrites the output
directory with a deterministic portable research archive:

- `README.md` local index
- deterministic per-ledger JSON copies
- one brief, risk report, history report, decision report, and scenario report
  per input ledger
- `portfolio.md`
- `evidence-audit.md`
- `watchlist.md`
- `action-plan.md`
- `manifest.json`
- `archive-summary.json`

The manifest uses relative generated filenames only. The machine-readable
summary includes ledger counts, file counts, `tool_version`, `ledger_ids`,
`generated_files`, and SHA-256 hashes for every archive file except
`archive-summary.json` itself. `archive-summary.json` remains listed in
`generated_files`, but is excluded from `file_hashes` to avoid a recursive
self-hash. The archive intentionally contains no timestamps, absolute paths,
workflow files, or dependency files.

```bash
verify-archive <archive-dir>
```

The `verify-archive` command reads `manifest.json` and
`archive-summary.json`, verifies that every generated file exists, rejects
absolute or external generated paths, recomputes SHA-256 hashes for every
`file_hashes` entry, confirms that `archive-summary.json` is excluded from
`file_hashes` while remaining in `generated_files`, and rejects workflow or
dependency files. It prints a deterministic validation summary and exits 0 for
valid archives, 1 for content validation failures, and 2 for unreadable or
malformed archive inputs.

```bash
diff-archive <old-archive-dir> <new-archive-dir> --output archive-diff.md --json-output archive-diff.json
```

The `diff-archive` command first applies the same archive verification
semantics to both inputs. Unreadable or malformed archive inputs exit 2.
Archives that can be read but fail validation exit 1 and print deterministic
validation errors. When both archives are valid, the command compares manifest
`generated_files`, archive-summary `file_hashes`, `ledger_ids`, `tool_version`,
and file counts. It writes deterministic Markdown and JSON with added,
removed, changed, and unchanged file information plus old/new ledger IDs,
old/new tool versions, old/new file counts, and a `changed` or `unchanged`
status.

```bash
html-dashboard <ledger-a.json> <ledger-b.json> [...] --output-dir html-dashboard
```

The `html-dashboard` command loads and validates every input ledger before
writing output. It requires at least two ledgers and cleanly overwrites the
output directory with a static no-JS public demo:

- `index.html`
- `style.css`
- one HTML page per input ledger
- `portfolio.html`
- `evidence-audit.html`
- `watchlist.html`
- `action-plan.html`
- `manifest.json`

Per-ledger pages summarize the existing brief, risk, history, decision memo,
and scenario plan payloads. Portfolio, evidence audit, watchlist, and action
plan pages summarize the existing aggregate payloads. The manifest is
deterministic and contains only `generated_files`, `ledger_ids`, and
`tool_version`; it does not include timestamps. HTML escaping uses only the
Python standard library.

See `examples/output/` for checked-in CLI output fixtures generated from
`examples/oklo-ai-power.json`, `examples/leveraged-etf-discipline.json`, and
the prior/current comparison pair in `examples/oklo-ai-power-prior.json`.
