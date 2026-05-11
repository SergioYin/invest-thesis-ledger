# invest-thesis-ledger

A zero-dependency Python package and CLI for maintaining investment thesis
ledgers as JSON, then rendering deterministic briefs, risk reports, and review
timelines.

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
reviews: 1
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

All generated outputs are deterministic for the same input file.

## Ledger Format

Ledgers are JSON objects. The v0.1.0 required fields are:

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
- `checklist`

The formal v0.1.0 schema reference is in `docs/ledger-schema.md`.

See:

- `examples/oklo-ai-power.json`
- `examples/leveraged-etf-discipline.json`

## Demo Outputs

Checked-in deterministic CLI output fixtures are available under
`examples/output/`:

- `examples/output/oklo-ai-power-brief.md`
- `examples/output/oklo-ai-power-risk.md`
- `examples/output/oklo-ai-power-risk.json`
- `examples/output/oklo-ai-power-history.md`
- `examples/output/oklo-ai-power-history.json`

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

## Roadmap

- Add more report templates while keeping deterministic output.
- Add migration helpers for future ledger versions.
- Add richer thesis drift analysis using explicit prior/current assumptions.

## License

MIT. See `LICENSE`.
