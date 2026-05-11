"""Schema loading and validation for investment thesis ledgers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


Ledger = Dict[str, Any]


REQUIRED_TOP_LEVEL = {
    "ledger_version": str,
    "thesis_id": str,
    "title": str,
    "asset": dict,
    "created": str,
    "updated": str,
    "thesis": str,
    "sources": list,
    "assumptions": list,
    "risks": list,
    "reviews": list,
}

REQUIRED_ASSET = {
    "name": str,
    "type": str,
    "ticker": str,
}

REQUIRED_SOURCE = {
    "id": str,
    "title": str,
    "publisher": str,
    "date": str,
    "url": str,
}

REQUIRED_ASSUMPTION = {
    "id": str,
    "statement": str,
    "confidence": str,
    "source_ids": list,
}

REQUIRED_RISK = {
    "id": str,
    "name": str,
    "severity": str,
    "probability": str,
    "mitigation": str,
    "source_ids": list,
}

REQUIRED_REVIEW = {
    "date": str,
    "decision": str,
    "summary": str,
    "source_ids": list,
}


def load_ledger(path: str | Path) -> Ledger:
    """Load a JSON ledger from disk."""

    ledger_path = Path(path)
    with ledger_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("ledger root must be a JSON object")
    return data


def validate_ledger(ledger: Mapping[str, Any]) -> Tuple[List[str], List[str]]:
    """Return validation errors and warnings for a ledger object."""

    errors: List[str] = []
    warnings: List[str] = []

    _require_fields("ledger", ledger, REQUIRED_TOP_LEVEL, errors)
    if errors:
        return errors, warnings

    if ledger.get("ledger_version") != "0.1.0":
        warnings.append("ledger.ledger_version is not 0.1.0")

    asset = ledger["asset"]
    _require_fields("ledger.asset", asset, REQUIRED_ASSET, errors)

    source_ids = _validate_list_items("ledger.sources", ledger["sources"], REQUIRED_SOURCE, errors)
    _validate_unique_ids("ledger.sources", source_ids, errors)
    source_id_set = set(source_ids)

    assumption_ids = _validate_list_items(
        "ledger.assumptions", ledger["assumptions"], REQUIRED_ASSUMPTION, errors
    )
    _validate_unique_ids("ledger.assumptions", assumption_ids, errors)

    risk_ids = _validate_list_items("ledger.risks", ledger["risks"], REQUIRED_RISK, errors)
    _validate_unique_ids("ledger.risks", risk_ids, errors)

    review_dates = []
    for index, review in enumerate(ledger["reviews"]):
        path = f"ledger.reviews[{index}]"
        if not isinstance(review, dict):
            errors.append(f"{path} must be an object")
            continue
        _require_fields(path, review, REQUIRED_REVIEW, errors)
        if isinstance(review.get("date"), str):
            review_dates.append(review["date"])
        if "drift" in review and not isinstance(review["drift"], str):
            errors.append(f"{path}.drift must be a string")
        _validate_source_refs(path, review.get("source_ids", []), source_id_set, errors)

    if review_dates != sorted(review_dates):
        warnings.append("ledger.reviews are not sorted by date")

    for index, assumption in enumerate(ledger["assumptions"]):
        if isinstance(assumption, dict):
            _validate_source_refs(
                f"ledger.assumptions[{index}]", assumption.get("source_ids", []), source_id_set, errors
            )

    for index, risk in enumerate(ledger["risks"]):
        if isinstance(risk, dict):
            _validate_source_refs(f"ledger.risks[{index}]", risk.get("source_ids", []), source_id_set, errors)

    for optional_list in ("positions", "catalysts", "checklist"):
        if optional_list in ledger and not isinstance(ledger[optional_list], list):
            errors.append(f"ledger.{optional_list} must be a list")

    return errors, warnings


def validation_summary(ledger: Mapping[str, Any], errors: Sequence[str], warnings: Sequence[str]) -> str:
    """Build deterministic validation output."""

    lines = [
        f"ledger: {ledger.get('thesis_id', '<unknown>')}",
        f"title: {ledger.get('title', '<unknown>')}",
        f"sources: {len(ledger.get('sources', [])) if isinstance(ledger.get('sources'), list) else 0}",
        f"assumptions: {len(ledger.get('assumptions', [])) if isinstance(ledger.get('assumptions'), list) else 0}",
        f"risks: {len(ledger.get('risks', [])) if isinstance(ledger.get('risks'), list) else 0}",
        f"reviews: {len(ledger.get('reviews', [])) if isinstance(ledger.get('reviews'), list) else 0}",
        f"status: {'valid' if not errors else 'invalid'}",
    ]
    lines.extend(f"warning: {warning}" for warning in warnings)
    lines.extend(f"error: {error}" for error in errors)
    return "\n".join(lines) + "\n"


def source_lookup(ledger: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    """Return sources keyed by source id."""

    return {
        source["id"]: source
        for source in ledger.get("sources", [])
        if isinstance(source, dict) and isinstance(source.get("id"), str)
    }


def _require_fields(path: str, value: Any, required: Mapping[str, type], errors: List[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return
    for key, expected_type in required.items():
        if key not in value:
            errors.append(f"{path}.{key} is required")
            continue
        if not isinstance(value[key], expected_type):
            errors.append(f"{path}.{key} must be {expected_type.__name__}")


def _validate_list_items(
    path: str, values: Any, required: Mapping[str, type], errors: List[str]
) -> List[str]:
    ids: List[str] = []
    if not isinstance(values, list):
        errors.append(f"{path} must be a list")
        return ids
    for index, value in enumerate(values):
        item_path = f"{path}[{index}]"
        if not isinstance(value, dict):
            errors.append(f"{item_path} must be an object")
            continue
        _require_fields(item_path, value, required, errors)
        item_id = value.get("id")
        if isinstance(item_id, str):
            ids.append(item_id)
    return ids


def _validate_unique_ids(path: str, ids: Iterable[str], errors: List[str]) -> None:
    seen = set()
    for item_id in ids:
        if item_id in seen:
            errors.append(f"{path} has duplicate id {item_id}")
        seen.add(item_id)


def _validate_source_refs(path: str, refs: Any, source_ids: set[str], errors: List[str]) -> None:
    if not isinstance(refs, list):
        errors.append(f"{path}.source_ids must be a list")
        return
    for ref in refs:
        if not isinstance(ref, str):
            errors.append(f"{path}.source_ids entries must be strings")
        elif ref not in source_ids:
            errors.append(f"{path}.source_ids references unknown source {ref}")
