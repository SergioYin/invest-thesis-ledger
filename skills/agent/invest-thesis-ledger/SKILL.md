---
name: invest-thesis-ledger
description: Use this skill when an agent needs to turn stock, ETF, IPO, or investment-theme research into a structured thesis ledger, then generate briefs, risk reports, decision memos, scenario plans, portfolio reviews, watchlists, action plans, archives, or HTML dashboards using the invest-thesis-ledger CLI.
version: 1.0.0
author: SergioYin + automation contributors
license: MIT
metadata:
  tags: [finance, investing, thesis-ledger, portfolio-review, decision-memo, cli]
  homepage: https://github.com/SergioYin/invest-thesis-ledger
---

# invest-thesis-ledger Agent Skill

## Purpose

Use the local `invest-thesis-ledger` CLI to maintain source-attributed investment thesis ledgers and generate deterministic research artifacts.

This file is an agent-facing operating protocol. The repository contains the executable tool; this skill tells compatible agents when and how to use it.

## Trigger When

Load this skill when a user asks to:

- organize stock, ETF, IPO, or investment-theme research into a durable thesis record;
- generate a pre-trade or pre-review decision memo;
- produce a risk report;
- create a base/bull/bear scenario plan;
- review thesis history or compare thesis drift across snapshots;
- build a weekly portfolio review, watchlist, review queue, or action plan;
- archive a research package or render a static HTML dashboard;
- preserve evidence, risks, catalysts, assumptions, position rules, or review notes instead of answering as a one-off chat.

## Runtime

From a repository checkout:

```bash
python -m invest_thesis_ledger --version
```

Optional local install:

```bash
python -m pip install .
invest-thesis-ledger --version
```

The tool is designed to be stdlib-only at runtime.

## Decision Tree

1. Raw research notes need to become a ledger
   - Find or create a JSON ledger.
   - If no ledger exists, start with:
     ```bash
     python -m invest_thesis_ledger init-template --asset <TICKER> --name "<Name>" --type <equity|etf|ipo|theme> --output <ledger>.json
     ```
   - Add sources, assumptions, risks, catalysts, reviews, and position rules before generating downstream reports.

2. User wants a concise research summary
   - Use `brief`.

3. User asks about risk, drawdown, concentration, overheat, or reasons not to proceed
   - Use `risk`; add `scenario-plan` for decision-related questions.

4. User is considering a buy, sell, add, reduce, or hold decision
   - Use `decision-memo` plus `risk` and `scenario-plan`.
   - Present the result as a checklist and research summary, not financial advice.

5. User asks for weekly review, watchlist, or next research actions
   - Use `portfolio`, `evidence-audit`, `review-queue`, `watchlist`, and/or `action-plan` across multiple ledgers.

6. User asks to preserve, share, or export a research package
   - Use `archive`, `verify-archive`, and optionally `html-dashboard`.

7. User asks whether a thesis changed over time
   - Use `history` for one ledger or `compare` for two ledger snapshots.

## Common Commands

Validate a ledger:

```bash
python -m invest_thesis_ledger validate examples/oklo-ai-power.json
```

Generate a brief:

```bash
python -m invest_thesis_ledger brief <ledger.json> --output brief.md
```

Generate a risk report:

```bash
python -m invest_thesis_ledger risk <ledger.json> --output risk.md --json-output risk.json
```

Generate a decision memo:

```bash
python -m invest_thesis_ledger decision-memo <ledger.json> --output decision-memo.md --json-output decision-memo.json
```

Generate a scenario plan:

```bash
python -m invest_thesis_ledger scenario-plan <ledger.json> --output scenario-plan.md --json-output scenario-plan.json
```

Portfolio-level review:

```bash
python -m invest_thesis_ledger portfolio <ledger1.json> <ledger2.json> --output portfolio.md --json-output portfolio.json
python -m invest_thesis_ledger evidence-audit <ledger1.json> <ledger2.json> --output audit.md --json-output audit.json
python -m invest_thesis_ledger review-queue <ledger1.json> <ledger2.json> --output review-queue.md --json-output review-queue.json
python -m invest_thesis_ledger watchlist <ledger1.json> <ledger2.json> --output watchlist.md --json-output watchlist.json
python -m invest_thesis_ledger action-plan <ledger1.json> <ledger2.json> --output action-plan.md --json-output action-plan.json
```

Archive and verify:

```bash
python -m invest_thesis_ledger archive <ledger1.json> <ledger2.json> --output-dir research-archive
python -m invest_thesis_ledger verify-archive research-archive
```

HTML dashboard:

```bash
python -m invest_thesis_ledger html-dashboard <ledger1.json> <ledger2.json> --output-dir html-dashboard
```

## Response Guidelines

When reporting generated artifacts to a user:

- Keep the summary concise unless the user asks for full generated files.
- Include generated file paths.
- Highlight decision-relevant items: thesis, evidence quality, key risks, invalidation conditions, position discipline, and unresolved information gaps.
- Avoid wide tables in chat surfaces that render tables poorly.

## Safety and Finance Boundaries

- Treat outputs as research organization and decision support, not investment advice.
- Do not claim the tool predicts returns or determines whether to buy or sell.
- For leveraged ETFs, explain daily-reset/path-dependence risk and position-size discipline.
- Do not fabricate sources. If source evidence is missing or stale, mark it as an information gap.
- Do not connect to brokerage accounts or place trades.

## Verification Checklist

Before reporting that generated artifacts are ready, run the relevant subset:

```bash
python -m invest_thesis_ledger validate <ledger.json>
python scripts/selfcheck.py
python -m unittest discover -s tests
python -m compileall invest_thesis_ledger tests scripts
git diff --check
```

For archives:

```bash
python -m invest_thesis_ledger verify-archive <archive-dir>
```

For releases or public repository changes:

```bash
git status --short
gh release view <tag> --json tagName,name,url,publishedAt,targetCommitish
```

## Done Criteria

A task using this skill is complete when:

- The ledger exists and validates, or the limitation is explicitly reported.
- Requested Markdown/JSON/HTML/archive artifacts were generated and their paths are known.
- The final summary explains the result and unresolved risks or information gaps.
- Any archive was verified.
- No output is framed as personalized financial advice.
