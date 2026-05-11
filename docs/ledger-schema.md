# Ledger Schema v0.4.0

This document defines the JSON ledger format accepted by `invest-thesis-ledger`
v0.4.0. Ledgers are research organization records only and are not investment
advice.

## Document Shape

A ledger is a single JSON object. The CLI validates required fields, required
nested object fields, duplicate IDs, source references, and a few basic type
constraints. Unknown fields are allowed so teams can keep local annotations
without breaking the renderer.

## Required Top-Level Fields

| Field | Type | Description |
| --- | --- | --- |
| `ledger_version` | string | Schema version. v0.4.0 ledgers should use `"0.4.0"`. v0.1.0, v0.2.0, and v0.3.0 remain accepted for compatibility; other values validate with a warning. |
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
| `positions` | array | `brief` | Position notes or sizing discipline. |
| `catalysts` | array | `brief`, `calendar`, `evidence` | Catalysts or evidence that could change conviction. |
| `broker_views` | array | `broker-matrix`, `evidence` | Broker, desk, or institution rating/target/thesis views. |
| `position_rules` | array | `exposure`, `evidence` | Position sizing, exposure, and trade discipline rules. |
| `checklist` | array | `risk` | Risk checklist items. |

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

## Determinism

For the same input file or ordered input file list, v0.4.0 CLI outputs are
deterministic:

- JSON outputs are serialized with sorted keys and two-space indentation.
- History reviews are sorted by review date.
- Calendar catalysts are sorted by date presence, date, window, and ID.
- Broker views are sorted by institution and ID.
- Position rules are sorted by ID, and exposure risk tags are sorted by tag.
- Portfolio assets are sorted by ticker and ledger ID.
- Portfolio catalyst and stale-source lists are sorted by stable ledger and
  item fields.
- Evidence stale-source warnings are measured against ledger `updated`, not the
  current wall-clock date.
- Source reference lists preserve the ledger order inside each item.
- Rendered source sections are sorted by source ID.
- `init-template` uses fixed placeholder dates so repeated runs with the same
  arguments produce byte-identical JSON.

## v0.4.0 Reports

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

`init-template --asset TICKER --name NAME --type TYPE --output ledger.json`
writes a deterministic starter ledger with v0.4.0 fields, fixed placeholder
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

See `examples/output/` for checked-in CLI output fixtures generated from
`examples/oklo-ai-power.json`, `examples/leveraged-etf-discipline.json`, and
the prior/current comparison pair in `examples/oklo-ai-power-prior.json`.
