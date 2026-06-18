"""Deterministic decision review walkthrough payloads."""

from __future__ import annotations

import hashlib
import html
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


def visual_walkthrough_payload(root: Optional[Union[str, Path]] = None) -> dict[str, Any]:
    """Build a deterministic visual walkthrough payload from local artifacts."""

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

    route = _visual_route()
    screenshots = _visual_screenshots(route)
    linked_artifacts = [
        _file_hash(root_path, root_path / "examples" / "output" / "html-dashboard" / "index.html"),
        _file_hash(root_path, root_path / "examples" / "output" / "oklo-ai-power-decision-review-pack.md"),
        _file_hash(root_path, root_path / "examples" / "output" / "evidence-path-receipt.md"),
        _file_hash(root_path, root_path / "examples" / "output" / "evidence-path-receipt.json"),
    ]
    boundary_text = (
        "This visual walkthrough is a deterministic screenshot guide generated from checked-in fixture "
        "labels and local artifact paths only. It does not capture live websites, fetch market data, "
        "connect to broker or account systems, place orders, execute trades, or provide investment advice."
    )
    static_text = _static_text(
        [step["command"] for step in route],
        fixture_paths,
        root_path,
        linked_artifacts + screenshots,
        boundary_text,
    )

    return {
        "walkthrough": {
            "workflow": "bounded visual walkthrough screenshot guide",
            "tool_version": __version__,
            "deterministic": True,
            "zero_dependencies": True,
            "fixture_source": "checked-in demo ledgers",
            "visual_format": "local SVG screenshot guide",
        },
        "route": route,
        "fixture_inputs": [_file_hash(root_path, path) for path in fixture_paths],
        "linked_artifacts": linked_artifacts,
        "visual_assets": screenshots,
        "hygiene_checks": {
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


def visual_walkthrough_files(root: Optional[Union[str, Path]] = None) -> list[tuple[str, str]]:
    """Return deterministic visual walkthrough files for an output directory."""

    payload = visual_walkthrough_payload(root)
    files = [
        ("README.md", render_visual_walkthrough(payload)),
        ("visual-walkthrough.json", to_json(payload)),
    ]
    files.extend(
        (step["visual_asset"], _visual_svg(index, step))
        for index, step in enumerate(payload["route"], start=1)
    )
    return files


def render_visual_walkthrough(payload: Mapping[str, Any]) -> str:
    """Render the deterministic visual walkthrough guide as Markdown."""

    walkthrough = payload["walkthrough"]
    lines = [
        "# Visual Walkthrough Screenshot Guide",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Workflow: {_inline(walkthrough['workflow'])}",
        f"- Tool version: {_inline(walkthrough['tool_version'])}",
        f"- Deterministic: {_yes_no(walkthrough['deterministic'])}",
        f"- Zero dependencies: {_yes_no(walkthrough['zero_dependencies'])}",
        f"- Fixture source: {_inline(walkthrough['fixture_source'])}",
        f"- Visual format: {_inline(walkthrough['visual_format'])}",
        "",
        "## Route",
        "",
    ]
    for step in payload["route"]:
        lines.append(f"### {_inline(step['step'])}")
        lines.append("")
        lines.append(f"- View: {_inline(step['view'])}")
        lines.append(f"- Local artifact: `{step['artifact']}`")
        lines.append(f"- Command: `{step['command']}`")
        lines.append(f"- Visual asset: `{step['visual_asset']}`")
        lines.append("")
    lines.extend(["## Fixture Inputs", ""])
    for item in payload["fixture_inputs"]:
        lines.append(f"- `{item['path']}` ({item['bytes']} bytes; sha256 `{item['sha256']}`)")
    lines.extend(["", "## Linked Local Artifacts", ""])
    lines.extend(["| Path | Bytes | SHA-256 |", "| --- | ---: | --- |"])
    for item in payload["linked_artifacts"]:
        lines.append(f"| `{item['path']}` | {item['bytes']} | `{item['sha256']}` |")
    lines.extend(["", "## Visual Assets", ""])
    lines.extend(["| Path | Kind | Bytes | SHA-256 |", "| --- | --- | ---: | --- |"])
    for item in payload["visual_assets"]:
        lines.append(f"| `{item['path']}` | {_inline(item['kind'])} | {item['bytes']} | `{item['sha256']}` |")
    lines.extend(["", "## Hygiene Checks", ""])
    for name, result in payload["hygiene_checks"].items():
        lines.append(f"- {_inline(name)}: {_inline(result['status'])}")
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


def _visual_route() -> list[dict[str, str]]:
    return [
        {
            "step": "dashboard_review",
            "view": "Open the static no-JS dashboard index and inspect the local review queue.",
            "artifact": "examples/output/html-dashboard/index.html",
            "command": (
                "python -m invest_thesis_ledger html-dashboard examples/oklo-ai-power.json "
                "examples/leveraged-etf-discipline.json --output-dir examples/output/html-dashboard"
            ),
            "visual_asset": "dashboard-route.svg",
        },
        {
            "step": "decision_review_pack",
            "view": "Open the Oklo decision review pack and review evidence, risks, catalysts, and questions.",
            "artifact": "examples/output/oklo-ai-power-decision-review-pack.md",
            "command": (
                "python -m invest_thesis_ledger decision-review-pack examples/oklo-ai-power.json "
                "--output examples/output/oklo-ai-power-decision-review-pack.md "
                "--json-output examples/output/oklo-ai-power-decision-review-pack.json"
            ),
            "visual_asset": "decision-review-pack-route.svg",
        },
        {
            "step": "evidence_path_receipt",
            "view": "Open the evidence path receipt and confirm linked receipts, hashes, and boundaries.",
            "artifact": "examples/output/evidence-path-receipt.md",
            "command": (
                "python -m invest_thesis_ledger evidence-path-receipt "
                "--output examples/output/evidence-path-receipt.md "
                "--json-output examples/output/evidence-path-receipt.json"
            ),
            "visual_asset": "evidence-path-route.svg",
        },
    ]


def _visual_screenshots(route: Sequence[Mapping[str, str]]) -> list[dict[str, Any]]:
    assets = []
    for index, step in enumerate(route, start=1):
        content = _visual_svg(index, step)
        encoded = content.encode("utf-8")
        assets.append(
            {
                "path": step["visual_asset"],
                "kind": "svg-screenshot-guide",
                "bytes": len(encoded),
                "sha256": hashlib.sha256(encoded).hexdigest(),
            }
        )
    return assets


def _visual_svg(index: int, step: Mapping[str, str]) -> str:
    title = _svg_text(step["step"].replace("_", " ").title())
    artifact = _svg_text(step["artifact"])
    view_lines = _svg_tspans(step["view"], 384, 188, 22, 66)
    command_lines = _svg_tspans(step["command"], 384, 350, 20, 74)
    return "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540" role="img">',
            f"  <title>{title}</title>",
            "  <rect width=\"960\" height=\"540\" fill=\"#f8fafc\"/>",
            "  <rect x=\"36\" y=\"32\" width=\"888\" height=\"476\" rx=\"8\" fill=\"#ffffff\" stroke=\"#334155\"/>",
            "  <rect x=\"36\" y=\"32\" width=\"888\" height=\"56\" rx=\"8\" fill=\"#0f172a\"/>",
            f"  <text x=\"64\" y=\"68\" font-family=\"Arial, sans-serif\" font-size=\"22\" fill=\"#ffffff\">Step {index}: {title}</text>",
            "  <rect x=\"64\" y=\"116\" width=\"260\" height=\"318\" rx=\"6\" fill=\"#e2e8f0\" stroke=\"#64748b\"/>",
            "  <text x=\"84\" y=\"152\" font-family=\"Arial, sans-serif\" font-size=\"16\" fill=\"#0f172a\">Local artifact</text>",
            f"  <text x=\"84\" y=\"188\" font-family=\"Arial, sans-serif\" font-size=\"14\" fill=\"#334155\">{artifact}</text>",
            "  <rect x=\"356\" y=\"116\" width=\"504\" height=\"132\" rx=\"6\" fill=\"#ecfeff\" stroke=\"#0891b2\"/>",
            "  <text x=\"384\" y=\"152\" font-family=\"Arial, sans-serif\" font-size=\"16\" fill=\"#0f172a\">Reviewer focus</text>",
            "  <text font-family=\"Arial, sans-serif\" font-size=\"14\" fill=\"#334155\">",
            *view_lines,
            "  </text>",
            "  <rect x=\"356\" y=\"278\" width=\"504\" height=\"156\" rx=\"6\" fill=\"#f1f5f9\" stroke=\"#64748b\"/>",
            "  <text x=\"384\" y=\"314\" font-family=\"Arial, sans-serif\" font-size=\"16\" fill=\"#0f172a\">Rerun command</text>",
            "  <text font-family=\"Arial, sans-serif\" font-size=\"12\" fill=\"#334155\">",
            *command_lines,
            "  </text>",
            "  <text x=\"64\" y=\"478\" font-family=\"Arial, sans-serif\" font-size=\"13\" fill=\"#475569\">Deterministic local SVG guide. No live data, no broker connection, not investment advice.</text>",
            "</svg>",
            "",
        ]
    )


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


def _svg_text(value: object) -> str:
    return html.escape(str(value).replace("\n", " "), quote=True)


def _svg_tspans(value: object, x: int, y: int, line_height: int, width: int) -> list[str]:
    lines = _wrap_words(str(value).replace("\n", " "), width)
    return [
        f"    <tspan x=\"{x}\" y=\"{y + (line_height * index)}\">{_svg_text(line)}</tspan>"
        for index, line in enumerate(lines)
    ]


def _wrap_words(value: str, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in value.split():
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines or [""]
