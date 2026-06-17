"""Deterministic decision review walkthrough payloads."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, Union

from . import __version__
from .hygiene import public_fixture_hygiene_issues
from .render import (
    decision_review_pack_payload,
    evidence_payload,
    render_decision_review_pack,
    render_evidence,
    render_review_queue,
    review_queue_payload,
    to_json,
)
from .schema import load_ledger, validate_ledger, validation_summary


def decision_review_walkthrough_payload(root: Optional[Union[str, Path]] = None) -> dict[str, Any]:
    """Build a deterministic walkthrough from the checked-in demo ledgers."""

    root_path = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    fixture_paths = [
        root_path / "examples" / "oklo-ai-power.json",
        root_path / "examples" / "leveraged-etf-discipline.json",
    ]
    ledgers = [load_ledger(str(path)) for path in fixture_paths]
    for ledger in ledgers:
        errors, warnings = validate_ledger(ledger)
        if errors:
            raise ValueError(validation_summary(ledger, errors, warnings))

    commands = _walkthrough_commands()
    artifacts = _walkthrough_artifacts(ledgers)
    hygiene_issues = public_fixture_hygiene_issues(root_path)
    boundary_text = (
        "This walkthrough uses checked-in demo ledger fixtures and deterministic local renderers only. "
        "It does not fetch live market data, does not connect to broker or account systems, does not "
        "place orders, and is not investment advice."
    )
    static_text = _static_text(commands, fixture_paths, root_path, artifacts, boundary_text)

    return {
        "walkthrough": {
            "workflow": "bounded decision review walkthrough",
            "tool_version": __version__,
            "deterministic": True,
            "zero_dependencies": True,
            "fixture_source": "checked-in demo ledgers",
        },
        "rerun_commands": commands,
        "fixture_inputs": [_file_hash(root_path, path) for path in fixture_paths],
        "generated_artifacts": artifacts,
        "stale_date_hygiene": {
            "status": "pass"
            if not any("is after ledger.updated" in issue for issue in hygiene_issues)
            else "fail",
            "issues": [issue for issue in hygiene_issues if "is after ledger.updated" in issue],
        },
        "hygiene_checks": {
            "public_fixture_hygiene": _check_result(not hygiene_issues, hygiene_issues),
            "not_investment_advice_notice": _check_result(
                not any("missing not-investment-advice notice" in issue for issue in hygiene_issues),
                [issue for issue in hygiene_issues if "missing not-investment-advice notice" in issue],
            ),
            "advice_wording": _check_result(
                not any("recommendation wording" in issue for issue in hygiene_issues),
                [issue for issue in hygiene_issues if "recommendation wording" in issue],
            ),
            "portable_paths": _check_result(not _has_private_path(static_text), []),
            "secret_terms": _check_result(not _has_secret_term(static_text), []),
        },
        "boundaries": {
            "no_live_market_data": True,
            "no_broker_connection": True,
            "no_account_data": True,
            "no_orders": True,
            "no_trading_execution": True,
            "not_investment_advice": True,
            "text": boundary_text,
        },
    }


def render_decision_review_walkthrough(payload: Mapping[str, Any]) -> str:
    """Render a deterministic decision review walkthrough as Markdown."""

    walkthrough = payload["walkthrough"]
    lines = [
        "# Decision Review Walkthrough",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Workflow: {_inline(walkthrough['workflow'])}",
        f"- Tool version: {_inline(walkthrough['tool_version'])}",
        f"- Deterministic: {_yes_no(walkthrough['deterministic'])}",
        f"- Zero dependencies: {_yes_no(walkthrough['zero_dependencies'])}",
        f"- Fixture source: {_inline(walkthrough['fixture_source'])}",
        "",
        "## Exact Rerun Commands",
        "",
    ]
    for command in payload["rerun_commands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Fixture Inputs", ""])
    for item in payload["fixture_inputs"]:
        lines.append(f"- `{item['path']}` ({item['bytes']} bytes; sha256 `{item['sha256']}`)")
    lines.extend(["", "## Generated Review and Evidence Artifacts", ""])
    lines.extend(["| Path | Kind | Bytes | SHA-256 |", "| --- | --- | ---: | --- |"])
    for item in payload["generated_artifacts"]:
        lines.append(f"| `{item['path']}` | {_inline(item['kind'])} | {item['bytes']} | `{item['sha256']}` |")
    stale = payload["stale_date_hygiene"]
    lines.extend(["", "## Stale-Date Hygiene", "", f"- Status: {_inline(stale['status'])}"])
    for issue in stale["issues"]:
        lines.append(f"- {_inline(issue)}")
    lines.extend(["", "## Hygiene Checks", ""])
    for name, result in payload["hygiene_checks"].items():
        lines.append(f"- {_inline(name)}: {_inline(result['status'])}")
        for issue in result["issues"]:
            lines.append(f"  - {_inline(issue)}")
    boundaries = payload["boundaries"]
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            f"- No live market data: {_yes_no(boundaries['no_live_market_data'])}",
            f"- No broker connection: {_yes_no(boundaries['no_broker_connection'])}",
            f"- No account data: {_yes_no(boundaries['no_account_data'])}",
            f"- No orders: {_yes_no(boundaries['no_orders'])}",
            f"- No trading execution: {_yes_no(boundaries['no_trading_execution'])}",
            f"- Not investment advice: {_yes_no(boundaries['not_investment_advice'])}",
            "",
            _inline(boundaries["text"]),
        ]
    )
    return "\n".join(lines) + "\n"


def _walkthrough_commands() -> list[str]:
    return [
        "python -m invest_thesis_ledger validate examples/oklo-ai-power.json",
        "python -m invest_thesis_ledger evidence examples/oklo-ai-power.json "
        "--output examples/output/oklo-ai-power-evidence.md "
        "--json-output examples/output/oklo-ai-power-evidence.json",
        "python -m invest_thesis_ledger decision-review-pack examples/oklo-ai-power.json "
        "--output examples/output/oklo-ai-power-decision-review-pack.md "
        "--json-output examples/output/oklo-ai-power-decision-review-pack.json",
        "python -m invest_thesis_ledger review-queue examples/oklo-ai-power.json "
        "examples/leveraged-etf-discipline.json --output examples/output/review-queue.md "
        "--json-output examples/output/review-queue.json",
        "python -m invest_thesis_ledger decision-review-walkthrough "
        "--output examples/output/decision-review-walkthrough.md "
        "--json-output examples/output/decision-review-walkthrough.json",
    ]


def _walkthrough_artifacts(ledgers: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    oklo = ledgers[0]
    review_provenance = {
        "workflow": "single-ledger decision-review-pack",
        "command": (
            "python -m invest_thesis_ledger decision-review-pack examples/oklo-ai-power.json "
            "--output oklo-ai-power-decision-review-pack.md "
            "--json-output oklo-ai-power-decision-review-pack.json"
        ),
        "argv": [
            "python",
            "-m",
            "invest_thesis_ledger",
            "decision-review-pack",
            "examples/oklo-ai-power.json",
            "--output",
            "oklo-ai-power-decision-review-pack.md",
            "--json-output",
            "oklo-ai-power-decision-review-pack.json",
        ],
        "input_ledger": "examples/oklo-ai-power.json",
        "markdown_output": "oklo-ai-power-decision-review-pack.md",
        "json_output": "oklo-ai-power-decision-review-pack.json",
    }
    generated = [
        ("examples/output/oklo-ai-power-evidence.md", render_evidence(oklo), "evidence"),
        ("examples/output/oklo-ai-power-evidence.json", to_json(evidence_payload(oklo)), "evidence"),
        (
            "examples/output/oklo-ai-power-decision-review-pack.md",
            render_decision_review_pack(oklo, provenance=review_provenance),
            "review",
        ),
        (
            "examples/output/oklo-ai-power-decision-review-pack.json",
            to_json(decision_review_pack_payload(oklo, provenance=review_provenance)),
            "review",
        ),
        ("examples/output/review-queue.md", render_review_queue(ledgers), "review"),
        ("examples/output/review-queue.json", to_json(review_queue_payload(ledgers)), "review"),
    ]
    return [
        {
            "path": path,
            "kind": kind,
            "bytes": len(text.encode("utf-8")),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        }
        for path, text, kind in sorted(generated, key=lambda item: item[0])
    ]


def _file_hash(root: Path, path: Path) -> dict[str, Any]:
    text = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": len(text),
        "sha256": hashlib.sha256(text).hexdigest(),
    }


def _check_result(passed: bool, issues: Sequence[str]) -> dict[str, Any]:
    return {"status": "pass" if passed else "fail", "issues": list(issues)}


def _static_text(
    commands: Sequence[str],
    fixture_paths: Sequence[Path],
    root: Path,
    artifacts: Sequence[Mapping[str, Any]],
    boundary_text: str,
) -> str:
    fields = list(commands)
    fields.extend(path.relative_to(root).as_posix() for path in fixture_paths)
    fields.extend(str(item["path"]) for item in artifacts)
    fields.extend(str(item["sha256"]) for item in artifacts)
    fields.append(boundary_text)
    return "\n".join(fields)


def _has_private_path(text: str) -> bool:
    import re

    return bool(re.search(r"/home/|/Users/|[A-Za-z]:\\", text))


def _has_secret_term(text: str) -> bool:
    import re

    return bool(re.search(r"\b(secret|password|api[_ -]?key|private key)\b", text, re.IGNORECASE))


def _yes_no(value: object) -> str:
    return "yes" if value is True else "no"


def _inline(value: object) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")
