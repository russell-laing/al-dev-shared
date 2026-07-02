"""Finding-to-ledger suppression matcher for health findings."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from .disposition_models import normalize_finding


SIMILARITY_THRESHOLD = 0.4
SIMILARITY_THRESHOLD_SAME_TYPE = 0.25
_SUBSTRING_MIN = 25
_OBJECT_SUFFICIENT_TYPES = {"naming", "name-fit"}
_WILDCARD = "unknown"
_KEBAB_RE = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)+")
_WORD_RE = re.compile(r"[a-z0-9]+")
_PREFIX_RE = re.compile(r"^[a-z][a-z0-9 /-]*:\s*")
_PATH_CITATION_RE = re.compile(
    r"^`?[a-z0-9_./-]+\.[a-z0-9]+(?::\d+(?:-\d+)?)?`?\s*(?:[—–-]+\s*)?"
)
_STOPWORDS = {
    "the",
    "a",
    "an",
    "of",
    "to",
    "in",
    "is",
    "it",
    "that",
    "this",
    "and",
    "or",
    "for",
    "with",
    "but",
    "not",
    "no",
    "are",
    "was",
    "its",
}


def object_members(cell: str) -> set[str]:
    return set(_KEBAB_RE.findall(cell.lower()))


def _is_table_separator_row(line: str) -> bool:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return bool(cells) and all(
        not cell or re.fullmatch(r":?-{3,}:?", cell) for cell in cells
    )


_TYPE_ALIASES = {
    "bloat": "bloat",
    "clarity": "clarity",
    "prompt clarity": "clarity",
    "structure": "structure",
    "structural": "structure",
    "structural conventions": "structure",
    "description": "description",
    "description drift": "description",
    "name fit": "name-fit",
    "name-fit": "name-fit",
    "naming": "naming",
    "naming convention": "naming",
    "tool hygiene": "tool-hygiene",
    "tool-hygiene": "tool-hygiene",
    "scope isolation": "scope-isolation",
    "model fit": "model-fit",
    "caller alignment": "caller-alignment",
    "usage patterns": "usage-patterns",
    "complexity": "complexity",
    "complexity outliers": "complexity",
    "handoff": "handoff",
    "handoff chain gaps": "handoff",
    "near-duplicate": "near-duplicate",
    "near-duplicate shapes": "near-duplicate",
    "pre-planning": "preplanning",
    "pre-planning skills": "preplanning",
    "shared execution backbone": "shared-backbone",
    "surface placement": "surface-placement",
}


def normalize_type(raw: str) -> str:
    key = re.sub(r"\s+", " ", raw.strip().lower()).rstrip("s")
    if key in _TYPE_ALIASES:
        return _TYPE_ALIASES[key]
    return _TYPE_ALIASES.get(raw.strip().lower(), "")


def _finding_type(text: str) -> str:
    head = normalize_finding(text)
    if ":" in head:
        label = head.split(":", 1)[0]
        if len(label) <= 32 and re.fullmatch(r"[A-Za-z][A-Za-z /-]*", label):
            return normalize_type(label)
    return ""


def _finding_tokens(text: str) -> set[str]:
    body = normalize_finding(text).lower()
    body = _PATH_CITATION_RE.sub("", body)
    body = _PREFIX_RE.sub("", body)
    return {t for t in _WORD_RE.findall(body) if len(t) >= 3 and t not in _STOPWORDS}


def _text_similar(a: str, b: str, threshold: float = SIMILARITY_THRESHOLD) -> bool:
    na, nb = normalize_finding(a).lower(), normalize_finding(b).lower()
    shorter = min(na, nb, key=len)
    if len(shorter) >= _SUBSTRING_MIN and (na in nb or nb in na):
        return True
    ta, tb = _finding_tokens(a), _finding_tokens(b)
    if not ta or not tb:
        return False
    overlap = len(ta & tb)
    union = len(ta | tb)
    return union > 0 and (overlap / union) >= threshold


def _field_compatible(finding_val: str, row_val: str) -> bool:
    fv, rv = finding_val.strip(), row_val.strip()
    return fv == rv or rv == _WILDCARD or fv == _WILDCARD


def _classification_for(disposition: str) -> str:
    d = disposition.strip().lower()
    if d in ("declined", "grandfathered"):
        return "suppress"
    if d == "fixed":
        return "verify"
    return "keep"


_PRECEDENCE = {"suppress": 0, "verify": 1, "keep": 2}


def match_against_ledger(
    findings: list[dict[str, str]], current_rows: list[dict[str, str]]
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for finding in findings:
        f_obj = finding.get("object", "").strip()
        f_type = finding.get("type", "") or _finding_type(finding.get("finding", ""))
        candidates: list[tuple[str, dict[str, str]]] = []
        for row in current_rows:
            if not _field_compatible(finding.get("surface", ""), row["surface"]):
                continue
            if not _field_compatible(finding.get("dimension", ""), row["dimension"]):
                continue
            members = object_members(row["object"])
            if f_obj and f_obj.lower() not in members and f_obj != row["object"].strip():
                continue
            r_type = _finding_type(row["finding"])
            same_type = bool(f_type) and f_type == r_type
            if f_type and r_type and f_type != r_type:
                continue
            if same_type and f_type in _OBJECT_SUFFICIENT_TYPES:
                pass
            else:
                threshold = (
                    SIMILARITY_THRESHOLD_SAME_TYPE if same_type else SIMILARITY_THRESHOLD
                )
                if not _text_similar(finding.get("finding", ""), row["finding"], threshold):
                    continue
            cls = _classification_for(row["disposition"])
            candidates.append((cls, row))
        candidates.sort(key=lambda x: (x[1].get("date", ""), -_PRECEDENCE[x[0]]), reverse=True)
        best = candidates[0] if candidates else None
        classification = best[0] if best else "keep"
        results.append(
            {
                "finding": finding,
                "classification": classification,
                "matched": best[1] if best else None,
            }
        )
    return results


def parse_findings_file(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    surface = _WILDCARD
    fm = re.search(r"^surface:\s*(\S+)\s*$", text, re.MULTILINE)
    if fm:
        surface = fm.group(1).strip()

    quality_kw = ("bloat", "clarity", "description", "name fit", "name-fit", "structural", "structure")
    findings: list[dict[str, str]] = []
    dimension = "design"
    ftype = ""
    parsed_count = 0
    for line in text.splitlines():
        header = re.match(r"^#{2,4}\s+(.*?)\s+Findings\b", line)
        if not header:
            # Bare-type headers (skill-lens output, e.g. "## Bloat") carry no
            # "Findings" suffix. Only treat them as section headers when the
            # title resolves to a known finding type — this excludes
            # unrelated headers like "## Raw lens output" or "## Failed lenses".
            bare = re.match(r"^#{2,4}\s+(.+?)\s*$", line)
            if bare:
                bare_title = re.sub(r"\s*\([^)]*\)\s*$", "", bare.group(1)).strip().lower()
                if normalize_type(bare_title):
                    header = bare
        if header:
            raw_title = header.group(1)
            title = re.sub(r"\s*\([^)]*\)\s*$", "", raw_title).lower()
            if "naming" in title:
                dimension = "naming"
            elif any(kw in title for kw in quality_kw):
                dimension = "quality"
            else:
                dimension = "design"
            ftype = normalize_type(title)
            continue
        item = re.match(r"^- \*\*(.+?)\*\*\s*\|(.*)$", line)
        if item:
            obj = item.group(1).strip()
            cells = [c.strip() for c in item.group(2).split("|")]
            observation = cells[1] if len(cells) >= 2 else (cells[0] if cells else "")
            findings.append(
                {
                    "surface": surface,
                    "dimension": dimension,
                    "object": obj,
                    "finding": observation,
                    "type": ftype,
                }
            )
            parsed_count += 1
            continue
        # Em-dash bullet format (skill-lens output), e.g.:
        #   - **document/SKILL.md:330-433** — text
        # No pipe separator; object is a file:line citation rather than a
        # bare name, so take the leading path segment as the object.
        dash_item = re.match(r"^- \*\*(.+?)\*\*\s*[—–]\s*(.*)$", line)
        if dash_item:
            obj = dash_item.group(1).strip().split("/")[0].strip()
            observation = dash_item.group(2).strip()
            findings.append(
                {
                    "surface": surface,
                    "dimension": dimension,
                    "object": obj,
                    "finding": observation,
                    "type": ftype,
                }
            )
            parsed_count += 1
        elif line.startswith("|") and not _is_table_separator_row(line) and not line.startswith("| Object") and not line.startswith("| Event"):
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) >= 2 and cols[0]:
                obj = cols[0]
                finding_text = cols[1] if len(cols) > 1 else ""
                findings.append(
                    {
                        "surface": surface,
                        "dimension": dimension,
                        "object": obj,
                        "finding": finding_text,
                        "type": ftype,
                    }
                )
                parsed_count += 1
    total_data_lines = sum(
        1
        for ln in text.splitlines()
        if ln.startswith("|")
        and not _is_table_separator_row(ln)
        and not ln.startswith("| Object")
        and not ln.startswith("| Event")
        and not ln.startswith("|---") and not ln.startswith("| ---")
    )
    if total_data_lines > 0 and parsed_count != total_data_lines:
        print(
            f"[parse_findings_file] WARNING: parsed {parsed_count} items but found {total_data_lines} "
            f"table rows — some rows may have malformed format; check parsing against specification",
            file=sys.stderr,
        )
    return findings
