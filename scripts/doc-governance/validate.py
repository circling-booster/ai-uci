#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[2]
DOC_DECISIONS = ROOT / "docs" / "decisions"
DOC_REPORTS = ROOT / "docs" / "reports"

ADR_ID_RE = re.compile(r"^ADR-\d{4}-\d{4}-.+$")
REPORT_ID_RE = re.compile(r"^RPT-\d{4}-(Q[1-4]|M(0[1-9]|1[0-2]))-\d{4}-.+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PERIOD_RE = re.compile(r"^\d{4}-(Q[1-4]|M(0[1-9]|1[0-2]))$")

ADR_STATUSES = {"Proposed", "Accepted", "Deprecated", "Superseded"}
ADR_DOMAINS = {"architecture", "product", "legal", "platform", "operations", "deprecated"}

REPORT_STATUSES = {"Draft", "Reviewed", "Approved"}
REPORT_DOMAINS = {
    "business",
    "product",
    "compliance",
    "architecture",
    "legal",
    "engineering",
    "strategy",
}
REPORT_TYPES = {
    "strategic",
    "technical",
    "legal",
    "product",
    "market",
    "risk",
    "compliance",
}

ADR_REQUIRED_FIELDS = {
    "id",
    "title",
    "status",
    "domain",
    "date",
    "owner",
    "reviewer",
    "approver",
    "related_adrs",
    "related_reports",
    "related_visions",
}

REPORT_REQUIRED_FIELDS = {
    "id",
    "title",
    "status",
    "type",
    "date",
    "period",
    "domain",
    "owner",
    "reviewer",
    "approver",
    "related_adrs",
}


class Issue:
    def __init__(self, severity: str, path: Path, message: str):
        self.severity = severity
        self.path = path
        self.message = message

    def __str__(self) -> str:
        return f"[{self.severity}] {self.path}: {self.message}"


def parse_scalar(raw: str) -> str:
    value = raw.strip()
    if value == "":
        return ""
    if value.lower() in {"null", "~", "none"}:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def parse_value(raw: str) -> Any:
    value = raw.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(v) for v in inner.split(",") if parse_scalar(v) != ""]
    return parse_scalar(value)


def parse_front_matter(text: str) -> Tuple[Dict[str, Any], List[str]]:
    lines = text.splitlines()
    issues: List[str] = []
    if not lines:
        return {}, ["No content"]
    if lines[0].strip() != "---":
        return {}, ["Missing front matter block"]

    metadata: Dict[str, Any] = {}
    key = None
    found_end = False

    for idx in range(1, len(lines)):
        line = lines[idx]
        stripped = line.rstrip()
        if stripped == "---":
            found_end = True
            break
        if not stripped.strip():
            continue
        if stripped.lstrip().startswith("-"):
            item_match = re.match(r"^\s*-\s*(.*)$", stripped)
            if item_match and key is not None and isinstance(metadata.get(key), list):
                metadata[key].append(parse_scalar(item_match.group(1)))
                continue
            issues.append(f"Line {idx + 1}: list item without active key: {stripped}")
            continue

        kv = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", stripped)
        if not kv:
            issues.append(f"Line {idx + 1}: invalid front matter line: {stripped}")
            key = None
            continue

        key, value = kv.group(1), kv.group(2)
        if value == "":
            metadata[key] = []
            continue

        parsed = parse_value(value)
        if isinstance(parsed, str) and parsed.startswith("[") and parsed.endswith("]"):
            if parsed == "[]":
                metadata[key] = []
            else:
                issues.append(
                    f"Line {idx + 1}: unsupported collection syntax for key '{key}': {value}"
                )
                metadata[key] = []
        elif isinstance(parsed, list):
            metadata[key] = parsed
            key = key
        else:
            metadata[key] = parsed
            key = None

    if not found_end:
        issues.append("Missing closing front matter marker '---'")

    return metadata, issues


def is_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() == ""


def to_issue_path(file_path: Path, root: Path) -> str:
    try:
        return str(file_path.relative_to(root))
    except ValueError:
        return str(file_path)


def escape_table_cell(value: str) -> str:
    return value.replace("|", "&#124;")


def date_sort_value(value: str) -> int:
    if not DATE_RE.match(value):
        return 0
    return int(value.replace("-", ""))


def period_sort_value(value: str) -> int:
    # Higher numeric value = newer
    year = int(value[:4])
    slot = value[5:]
    if slot.startswith("Q"):
        return year * 100 + int(slot[1:]) + 100
    return year * 100 + int(slot[1:]) + 200


def issue(severity: str, issues: List[Issue], path: Path, message: str):
    issues.append(Issue(severity, path, message))


def iterate_markdown_candidates(base: Path, mode: str) -> List[Path]:
    if mode == "decisions":
        skip = {"templates", "registry"}
    else:
        skip = {"templates", "registry"}
    files = []
    for path in sorted(base.rglob("*.md")):
        rel = path.relative_to(base)
        parts = rel.parts
        if not parts:
            continue
        if parts[0] in skip:
            continue
        if len(parts) == 1:
            continue
        files.append(path)
    return files


def validate_adr_document(
    path: Path,
    rel_path: Path,
    metadata: Dict[str, Any],
    issue_list: List[Issue],
) -> Dict[str, Any]:
    for key in ADR_REQUIRED_FIELDS:
        if key not in metadata:
            issue("ERROR", issue_list, path, f"[ADR] missing required field '{key}'")
    if "id" in metadata and not isinstance(metadata["id"], str):
        issue("ERROR", issue_list, path, "[ADR] field 'id' must be a string")
    if "id" in metadata and not ADR_ID_RE.match(metadata["id"]):
        issue("ERROR", issue_list, path, f"[ADR] invalid id format: '{metadata['id']}'")
    if "status" in metadata and metadata["status"] not in ADR_STATUSES:
        issue("ERROR", issue_list, path, f"[ADR] invalid status: '{metadata['status']}'")
    if "date" in metadata and not DATE_RE.match(metadata["date"]):
        issue("ERROR", issue_list, path, f"[ADR] invalid date format: '{metadata['date']}'")
    if "domain" in metadata and metadata["domain"] not in ADR_DOMAINS:
        issue("ERROR", issue_list, path, f"[ADR] invalid domain: '{metadata['domain']}'")
    if metadata.get("domain") != rel_path.parts[0]:
        issue(
            "ERROR",
            issue_list,
            path,
            f"[ADR] path domain '{rel_path.parts[0]}' does not match front matter domain '{metadata.get('domain')}'",
        )

    if metadata.get("status") == "Deprecated" and metadata.get("domain") != "deprecated":
        issue("WARN", issue_list, path, "[ADR] Deprecated ADR is usually placed under decisions/deprecated/")
    if metadata.get("status") != "Deprecated" and metadata.get("domain") == "deprecated":
        issue("WARN", issue_list, path, "[ADR] deprecated domain usually means status = Deprecated")

    for field in ("owner", "reviewer", "approver", "title"):
        if field in metadata and is_empty_string(metadata[field]):
            issue("ERROR", issue_list, path, f"[ADR] required field '{field}' is empty")

    for list_field in ("related_adrs", "related_reports", "related_visions", "supersedes", "superseded_by", "tags"):
        if list_field in metadata and not isinstance(metadata[list_field], list):
            issue("ERROR", issue_list, path, f"[ADR] '{list_field}' must be an array")

    if "supersedes" in metadata and not isinstance(metadata["supersedes"], list):
        issue("ERROR", issue_list, path, "[ADR] supersedes must be an array")
    if "superseded_by" in metadata and not isinstance(metadata["superseded_by"], list):
        issue("ERROR", issue_list, path, "[ADR] superseded_by must be an array")

    if "related_adrs" in metadata and metadata.get("related_adrs") == []:
        issue("WARN", issue_list, path, "[ADR] related_adrs is empty")

    return {
        "id": metadata.get("id", ""),
        "title": metadata.get("title", ""),
        "status": metadata.get("status", ""),
        "date": metadata.get("date", ""),
        "domain": metadata.get("domain", ""),
        "path": to_issue_path(path, ROOT),
        "metadata": metadata,
        "file_rel": rel_path,
    }


def validate_report_document(
    path: Path,
    rel_path: Path,
    metadata: Dict[str, Any],
    issue_list: List[Issue],
) -> Dict[str, Any]:
    for key in REPORT_REQUIRED_FIELDS:
        if key not in metadata:
            issue("ERROR", issue_list, path, f"[Report] missing required field '{key}'")

    if "quarter" in metadata:
        issue("WARN", issue_list, path, "[Report] legacy field 'quarter' is deprecated. Use 'period'.")

    if "id" in metadata and not isinstance(metadata["id"], str):
        issue("ERROR", issue_list, path, "[Report] field 'id' must be a string")
    if "id" in metadata and not REPORT_ID_RE.match(metadata["id"]):
        issue("ERROR", issue_list, path, f"[Report] invalid id format: '{metadata['id']}'")
    if "status" in metadata and metadata["status"] not in REPORT_STATUSES:
        issue("ERROR", issue_list, path, f"[Report] invalid status: '{metadata['status']}'")
    if "type" in metadata and metadata["type"] not in REPORT_TYPES:
        issue("ERROR", issue_list, path, f"[Report] invalid type: '{metadata['type']}'")
    if "date" in metadata and not DATE_RE.match(metadata["date"]):
        issue("ERROR", issue_list, path, f"[Report] invalid date format: '{metadata['date']}'")
    if "period" in metadata and not PERIOD_RE.match(metadata["period"]):
        issue("ERROR", issue_list, path, f"[Report] invalid period: '{metadata['period']}'")
    if "domain" in metadata and metadata["domain"] not in REPORT_DOMAINS:
        issue("ERROR", issue_list, path, f"[Report] invalid domain: '{metadata['domain']}'")
    for field in ("owner", "reviewer", "approver", "title"):
        if field in metadata and is_empty_string(metadata[field]):
            issue("ERROR", issue_list, path, f"[Report] required field '{field}' is empty")

    if "id" in metadata:
        m = re.match(r"^RPT-(\d{4})-((?:Q[1-4]|M(?:0[1-9]|1[0-2])))-\d{4}-.+$", metadata["id"])
        if m and "period" in metadata and metadata["period"] != m.group(2):
            issue(
                "ERROR",
                issue_list,
                path,
                f"[Report] id period '{m.group(2)}' does not match metadata period '{metadata['period']}'",
            )

    if rel_path.parts[0] not in {"by-domain", "by-quarter"}:
        issue("ERROR", issue_list, path, "[Report] file must be under by-domain/ or by-quarter/")
    elif rel_path.parts[0] == "by-domain":
        expected_domain = rel_path.parts[1] if len(rel_path.parts) > 1 else ""
        if "domain" in metadata and metadata["domain"] != expected_domain:
            issue(
                "ERROR",
                issue_list,
                path,
                f"[Report] path domain '{expected_domain}' does not match front matter domain '{metadata.get('domain')}'",
            )
    elif rel_path.parts[0] == "by-quarter":
        expected_period = rel_path.parts[1] if len(rel_path.parts) > 1 else ""
        if expected_period and not PERIOD_RE.match(expected_period):
            issue(
                "ERROR",
                issue_list,
                path,
                f"[Report] invalid by-quarter path period '{expected_period}'",
            )
        if "period" in metadata and expected_period and metadata["period"] != expected_period:
            issue(
                "ERROR",
                issue_list,
                path,
                f"[Report] path period '{expected_period}' does not match metadata period '{metadata.get('period')}'",
            )
        elif metadata.get("period") and metadata["period"] != "" and not expected_period:
            issue(
                "ERROR",
                issue_list,
                path,
                f"[Report] cannot validate period because by-quarter path is missing or invalid: '{rel_path}'",
            )

    if "related_adrs" in metadata and not isinstance(metadata["related_adrs"], list):
        issue("ERROR", issue_list, path, "[Report] related_adrs must be an array")

    return {
        "id": metadata.get("id", ""),
        "title": metadata.get("title", ""),
        "type": metadata.get("type", ""),
        "status": metadata.get("status", ""),
        "date": metadata.get("date", ""),
        "period": metadata.get("period", ""),
        "domain": metadata.get("domain", ""),
        "path": to_issue_path(path, ROOT),
        "metadata": metadata,
        "file_rel": rel_path,
    }


def validate_references(issues: List[Issue], adrs: List[Dict[str, Any]], reports: List[Dict[str, Any]]):
    adr_ids = {d["id"]: d["path"] for d in adrs if d.get("id")}
    report_ids = {d["id"]: d["path"] for d in reports if d.get("id")}
    all_adr_ids = set(adr_ids.keys())
    all_report_ids = set(report_ids.keys())
    visions_root = ROOT / "docs" / "visions"

    for doc in adrs:
        path = ROOT / doc["path"]
        meta = doc["metadata"]
        if "related_adrs" in meta:
            for related_id in meta["related_adrs"]:
                if not isinstance(related_id, str) or not ADR_ID_RE.match(related_id):
                    issue("ERROR", issues, Path(doc["path"]), f"[ADR] invalid related ADR id '{related_id}'")
                elif related_id not in all_adr_ids:
                    issue("ERROR", issues, Path(doc["path"]), f"[ADR] related ADR not found: '{related_id}'")
        if "related_reports" in meta:
            for related_id in meta["related_reports"]:
                if not isinstance(related_id, str) or not related_id.startswith("RPT-"):
                    issue("ERROR", issues, Path(doc["path"]), f"[ADR] invalid related Report id '{related_id}'")
                elif related_id not in all_report_ids:
                    issue("ERROR", issues, Path(doc["path"]), f"[ADR] related Report not found: '{related_id}'")
        if "related_visions" in meta:
            for related_path in meta["related_visions"]:
                if not isinstance(related_path, str) or not related_path:
                    issue("ERROR", issues, Path(doc["path"]), "[ADR] related_visions contains empty item")
                    continue
                full = visions_root / related_path
                if not full.exists():
                    issue("ERROR", issues, Path(doc["path"]), f"[ADR] related vision not found: '{related_path}'")

    for doc in reports:
        path = ROOT / doc["path"]
        meta = doc["metadata"]
        for related_id in meta.get("related_adrs", []):
            if not isinstance(related_id, str) or not ADR_ID_RE.match(related_id):
                issue("ERROR", issues, Path(doc["path"]), f"[Report] invalid related ADR id '{related_id}'")
            elif related_id not in all_adr_ids:
                issue("ERROR", issues, Path(doc["path"]), f"[Report] related ADR not found: '{related_id}'")


def build_indices(issues: List[Issue], adrs: List[Dict[str, Any]], reports: List[Dict[str, Any]]) -> List[str]:
    if any(i.severity == "ERROR" for i in issues):
        return []
    return [
        render_decision_index(adrs),
        render_report_index(reports),
    ]


def render_decision_index(adrs: List[Dict[str, Any]]) -> str:
    status_rank = {"Accepted": 4, "Proposed": 3, "Deprecated": 2, "Superseded": 1}
    sorted_items = sorted(
        adrs,
        key=lambda i: (
            status_rank.get(i.get("status"), 0),
            date_sort_value(i.get("date", "")),
            i.get("id", ""),
        ),
        reverse=True,
    )
    lines = [
        "# ADR 인덱스",
        "",
        "<!-- AUTO-GENERATED by scripts/doc-governance/validate.py. Do not edit manually. -->",
        "",
        "| ID | 제목 | 상태 | 도메인 | 작성일 | 관련 ADR/Report |",
        "|---|---|---|---|---|---|",
    ]
    for item in sorted_items:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_table_cell(item.get("id", "")),
                    f"[{escape_table_cell(item.get('title', ''))}](../../{item['path']})",
                    escape_table_cell(item.get("status", "")),
                    escape_table_cell(item.get("domain", "")),
                    escape_table_cell(item.get("date", "")),
                    ", ".join(item["metadata"].get("related_adrs", []))
                    + (" / " if item["metadata"].get("related_adrs") and item["metadata"].get("related_reports") else "")
                    + ", ".join(item["metadata"].get("related_reports", [])),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def render_report_index(reports: List[Dict[str, Any]]) -> str:
    status_rank = {"Approved": 3, "Reviewed": 2, "Draft": 1}
    sorted_items = sorted(
        reports,
        key=lambda i: (
            i.get("period", ""),
            status_rank.get(i.get("status"), 0),
            date_sort_value(i.get("date", "")),
            i.get("id", ""),
        ),
        reverse=True,
    )
    lines = [
        "# Report 인덱스",
        "",
        "<!-- AUTO-GENERATED by scripts/doc-governance/validate.py. Do not edit manually. -->",
        "",
        "| ID | 제목 | 유형 | 상태 | 도메인 | 작성일 | 관련 ADR |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in sorted_items:
        related_adrs = ", ".join(item["metadata"].get("related_adrs", []))
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_table_cell(item.get("id", "")),
                    f"[{escape_table_cell(item.get('title', ''))}](../../{item['path']})",
                    escape_table_cell(item.get("type", "")),
                    escape_table_cell(item.get("status", "")),
                    escape_table_cell(item.get("domain", "")),
                    escape_table_cell(item.get("date", "")),
                    escape_table_cell(related_adrs),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def validate_and_collect():
    issues: List[Issue] = []
    adrs: List[Dict[str, Any]] = []
    reports: List[Dict[str, Any]] = []
    id_count = defaultdict(int)

    # ADR documents
    for path in iterate_markdown_candidates(DOC_DECISIONS, "decisions"):
        rel = path.relative_to(DOC_DECISIONS)
        try:
            metadata, parse_issues = parse_front_matter(path.read_text(encoding="utf-8"))
        except OSError as err:
            issues.append(Issue("ERROR", path, f"[ADR] failed to read file: {err}"))
            continue
        for msg in parse_issues:
            issue("ERROR", issues, path, f"[ADR] {msg}")
        item = validate_adr_document(path, rel, metadata, issues)
        if item["id"]:
            id_count[item["id"]] += 1
            if id_count[item["id"]] > 1:
                issue("ERROR", issues, path, f"[ADR] duplicate id '{item['id']}'")
        adrs.append(item)

    # Report documents
    for path in iterate_markdown_candidates(DOC_REPORTS, "reports"):
        rel = path.relative_to(DOC_REPORTS)
        try:
            metadata, parse_issues = parse_front_matter(path.read_text(encoding="utf-8"))
        except OSError as err:
            issues.append(Issue("ERROR", path, f"[Report] failed to read file: {err}"))
            continue
        for msg in parse_issues:
            issue("ERROR", issues, path, f"[Report] {msg}")
        item = validate_report_document(path, rel, metadata, issues)
        if item["id"]:
            id_count[item["id"]] += 1
            if id_count[item["id"]] > 1:
                issue("ERROR", issues, path, f"[Report] duplicate id '{item['id']}'")
        reports.append(item)

    validate_references(issues, adrs, reports)
    return issues, adrs, reports


def write_indexes(decision_text: str, report_text: str):
    decision_path = DOC_DECISIONS / "registry" / "decisions-index.md"
    report_path = DOC_REPORTS / "registry" / "reports-index.md"
    decision_path.write_text(decision_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Validate ADR/Report documents and regenerate governance indices."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate documents and print issues",
    )
    parser.add_argument(
        "--generate-index",
        action="store_true",
        help="Generate registry index files after successful validation",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print success/error summary",
    )
    args = parser.parse_args()

    do_check = args.check or args.generate_index or (not args.check and not args.generate_index)
    issues, adrs, reports = validate_and_collect() if do_check else ([], [], [])

    if do_check:
        error_count = len([i for i in issues if i.severity == "ERROR"])
        warn_count = len([i for i in issues if i.severity == "WARN"])
        for i in issues:
            print(i)
        if args.summary:
            print(f"\nValidation summary: errors={error_count}, warnings={warn_count}")
            print(f"Found ADR docs: {len(adrs)}")
            print(f"Found reports: {len(reports)}")
        if error_count:
            return 1

    if args.generate_index:
        generated = build_indices(issues, adrs, reports)
        if not generated:
            if not do_check:
                print("[ERROR] cannot generate indices due to missing validation")
            return 1
        write_indexes(generated[0], generated[1])
        if args.summary:
            print("[OK] regenerated: docs/decisions/registry/decisions-index.md")
            print("[OK] regenerated: docs/reports/registry/reports-index.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
