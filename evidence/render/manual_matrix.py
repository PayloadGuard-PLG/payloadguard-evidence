"""Hand-built traceability matrix renderer.

This module is deliberately hand-written and reviewed before any automation
(Phase B) reuses its logic. Invariants:
  - Strength comes ONLY from the verification result, never from
    intended_method.
  - No matching result -> Strength.GAP plus an explanatory note.
  - intended_method != realized strength -> intent_matches_reality=False
    plus a note.
  - Every BOUNDED_CHECKED row renders its bounds and the caveat text.
  - No fabricated content anywhere.
"""

import datetime
from typing import Optional

from evidence.model import CAVEAT, RequirementBinding, Strength, VerificationResult

# Preference order when several results bind to one implementation.
_STRENGTH_PREFERENCE = [Strength.PROVEN, Strength.BOUNDED_CHECKED, Strength.TESTED]


def _pick_result(results: list, implementation: str) -> Optional[VerificationResult]:
    matching = [r for r in results if r.code_location == implementation]
    if not matching:
        return None
    for preferred in _STRENGTH_PREFERENCE:
        for r in matching:
            if r.strength is preferred:
                return r
    return matching[0]


def build_traceability_matrix(metadata: dict, results: list, tool_versions: Optional[dict] = None) -> tuple:
    """Bind metadata requirements to verification results.

    tool_versions is reporting context only (e.g. from a run manifest); it
    never influences binding or strength.

    Returns (matrix_dict, markdown_str).
    """
    tool_versions = tool_versions or {}
    rows = []
    bindings = []
    for req in metadata["requirements"]:
        result = _pick_result(results, req["implementation"])
        notes = []
        if result is None:
            strength = Strength.GAP
            notes.append("no verification result for this implementation")
        else:
            strength = result.strength
        intent_ok = req["intended_method"] == strength.value
        if not intent_ok:
            notes.append(f"intended {req['intended_method']}, realized {strength.value}")
        bindings.append(
            RequirementBinding(
                requirement_id=req["id"],
                requirement_text=req["text"].strip(),
                code_location=req["implementation"],
                result=result,
                intended_method=req["intended_method"],
                intent_matches_reality=intent_ok,
                notes=list(notes),
            )
        )
        rows.append(
            {
                "requirement_id": req["id"],
                "requirement_text": req["text"].strip(),
                "code_location": req["implementation"],
                "method": result.method if result else None,
                "strength": strength.value,
                "caveat": CAVEAT[strength],
                "result_status": result.raw_status if result else None,
                "bounds": result.bounds if result and strength is Strength.BOUNDED_CHECKED else None,
                "counterexample": result.counterexample if result else None,
                "intent_ok": intent_ok,
                "notes": notes,
            }
        )

    matrix = {
        "artifact": "IEC 62304 Traceability Matrix",
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "tool_versions": tool_versions,
        "crosshair_bounds": metadata["toolchain"]["crosshair_bounds"],
        "rows": rows,
    }
    return matrix, _render_markdown(matrix)


def _render_markdown(matrix: dict) -> str:
    def cell(value) -> str:
        return str(value).replace("|", "\\|") if value is not None else "—"

    lines = [
        "# IEC 62304 Traceability Matrix",
        "",
        f"Generated (UTC): {matrix['generated_utc']}",
        f"Tool versions: {matrix['tool_versions']}",
        f"CrossHair bounds: {matrix['crosshair_bounds']}",
        "",
        "| Requirement | Code | Method | Strength | Result | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for row in matrix["rows"]:
        notes = "; ".join(row["notes"]) if row["notes"] else "—"
        lines.append(
            "| {req} | {code} | {method} | {strength} | {result} | {notes} |".format(
                req=cell(row["requirement_id"]),
                code=cell(row["code_location"]),
                method=cell(row["method"]),
                strength=cell(row["strength"]),
                result=cell(row["result_status"]),
                notes=cell(notes),
            )
        )

    lines += ["", "## Caveats", ""]
    seen = []
    for row in matrix["rows"]:
        if row["strength"] not in seen:
            seen.append(row["strength"])
            lines.append(f"- **{row['strength']}**: {row['caveat']}")
            if row["strength"] == Strength.BOUNDED_CHECKED.value and row["bounds"]:
                lines.append(f"  - Bounds: {row['bounds']}")

    lines += ["", "## Notes", ""]
    any_note = False
    for row in matrix["rows"]:
        for note in row["notes"]:
            any_note = True
            lines.append(f"- {row['requirement_id']}: {note}")
    if not any_note:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)
