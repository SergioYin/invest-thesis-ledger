"""Deterministic Markdown and JSON renderers."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Sequence

from .schema import source_lookup


def render_brief(ledger: Mapping[str, Any]) -> str:
    """Render a source-attributed investment thesis brief."""

    asset = ledger["asset"]
    lines = [
        f"# {ledger['title']}",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        "## Asset",
        "",
        f"- Name: {asset['name']}",
        f"- Type: {asset['type']}",
        f"- Ticker: {asset['ticker']}",
        f"- Ledger ID: {ledger['thesis_id']}",
        f"- Updated: {ledger['updated']}",
        "",
        "## Thesis",
        "",
        ledger["thesis"],
        "",
        "## Assumptions",
        "",
    ]
    for item in ledger["assumptions"]:
        lines.append(
            f"- {item['id']}: {item['statement']} "
            f"(confidence: {item['confidence']}; sources: {_refs(item['source_ids'])})"
        )
    lines.extend(["", "## Catalysts", ""])
    for item in ledger.get("catalysts", []):
        lines.append(f"- {item}")
    if not ledger.get("catalysts"):
        lines.append("- None recorded.")
    lines.extend(["", "## Current Position Notes", ""])
    for item in ledger.get("positions", []):
        lines.append(f"- {item}")
    if not ledger.get("positions"):
        lines.append("- None recorded.")
    lines.extend(["", "## Sources", ""])
    lines.extend(_source_lines(ledger))
    return "\n".join(lines) + "\n"


def risk_payload(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    """Build deterministic structured risk output."""

    checklist = []
    for index, item in enumerate(ledger.get("checklist", []), start=1):
        if isinstance(item, dict):
            checklist.append(
                {
                    "id": item.get("id", f"C{index}"),
                    "item": item.get("item", ""),
                    "status": item.get("status", "open"),
                }
            )
        else:
            checklist.append({"id": f"C{index}", "item": str(item), "status": "open"})
    return {
        "thesis_id": ledger["thesis_id"],
        "title": ledger["title"],
        "updated": ledger["updated"],
        "risks": [
            {
                "id": item["id"],
                "name": item["name"],
                "severity": item["severity"],
                "probability": item["probability"],
                "mitigation": item["mitigation"],
                "source_ids": list(item["source_ids"]),
            }
            for item in ledger["risks"]
        ],
        "checklist": checklist,
    }


def render_risk(ledger: Mapping[str, Any]) -> str:
    """Render a Markdown risk and checklist report."""

    payload = risk_payload(ledger)
    lines = [
        f"# Risk Report: {payload['title']}",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Ledger ID: {payload['thesis_id']}",
        f"- Updated: {payload['updated']}",
        "",
        "## Risks",
        "",
    ]
    for item in payload["risks"]:
        lines.extend(
            [
                f"### {item['id']}: {item['name']}",
                "",
                f"- Severity: {item['severity']}",
                f"- Probability: {item['probability']}",
                f"- Mitigation: {item['mitigation']}",
                f"- Sources: {_refs(item['source_ids'])}",
                "",
            ]
        )
    lines.extend(["## Checklist", ""])
    for item in payload["checklist"]:
        lines.append(f"- [{_checkbox(item['status'])}] {item['id']}: {item['item']} ({item['status']})")
    if not payload["checklist"]:
        lines.append("- No checklist items recorded.")
    lines.extend(["", "## Sources", ""])
    lines.extend(_source_lines(ledger))
    return "\n".join(lines) + "\n"


def history_payload(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    """Build deterministic structured history output."""

    return {
        "thesis_id": ledger["thesis_id"],
        "title": ledger["title"],
        "created": ledger["created"],
        "updated": ledger["updated"],
        "reviews": [
            {
                "date": item["date"],
                "decision": item["decision"],
                "summary": item["summary"],
                "drift": item.get("drift", "none recorded"),
                "source_ids": list(item["source_ids"]),
            }
            for item in sorted(ledger["reviews"], key=lambda review: review["date"])
        ],
    }


def render_history(ledger: Mapping[str, Any]) -> str:
    """Render a Markdown review timeline and thesis drift report."""

    payload = history_payload(ledger)
    lines = [
        f"# History: {payload['title']}",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Ledger ID: {payload['thesis_id']}",
        f"- Created: {payload['created']}",
        f"- Updated: {payload['updated']}",
        "",
        "## Timeline",
        "",
    ]
    for item in payload["reviews"]:
        lines.extend(
            [
                f"### {item['date']} - {item['decision']}",
                "",
                f"- Summary: {item['summary']}",
                f"- Drift: {item['drift']}",
                f"- Sources: {_refs(item['source_ids'])}",
                "",
            ]
        )
    lines.extend(["## Sources", ""])
    lines.extend(_source_lines(ledger))
    return "\n".join(lines) + "\n"


def to_json(data: Mapping[str, Any]) -> str:
    """Serialize JSON deterministically."""

    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _refs(source_ids: Sequence[str]) -> str:
    return ", ".join(f"[{source_id}]" for source_id in source_ids) if source_ids else "none"


def _source_lines(ledger: Mapping[str, Any]) -> List[str]:
    sources = source_lookup(ledger)
    lines = []
    for source_id in sorted(sources):
        source = sources[source_id]
        lines.append(
            f"- [{source_id}] {source['title']}. {source['publisher']}, "
            f"{source['date']}. {source['url']}"
        )
    return lines


def _checkbox(status: str) -> str:
    return "x" if status.lower() in {"done", "closed", "passed", "complete"} else " "
