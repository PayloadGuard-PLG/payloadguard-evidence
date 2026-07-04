"""T4 variant binders/renderers — three parallel schema-fork views.

All variants bind the IDENTICAL underlying evidence: the Sample A CrossHair
capture (run_manifest.json) and the four concrete runs in
concrete_results.json (T4-0). They differ only in shape:

  Variant A: one row per requirement, evidence as a LIST of records.
  Variant B: one record per row; concrete runs are shadow pseudo-requirements
             with an explicit parent_requirement field.
  Variant C: one record per row; two independent artifacts partitioned by
             method (symbolic / concrete).

Shared discipline (unchanged from manual_matrix.py):
  - Strength comes ONLY from the evidence record, never from intended_method.
  - Caveat text comes from evidence.model.CAVEAT.
  - No fabricated content: binders refuse to run on failed captures.
  - Generated artifacts do not inline intended_method values; intent
    mismatches are flagged with intent_ok=false and a note referring to the
    authored metadata (see the T4 session constraint on generated tokens).
"""

import datetime

from evidence.model import CAVEAT, Strength

_ARTIFACT_TITLES = {
    "a": "IEC 62304 Traceability Matrix (variant A: evidence array per requirement)",
    "b": "IEC 62304 Traceability Matrix (variant B: flattened pseudo-requirements)",
    "c-symbolic": "IEC 62304 Traceability Matrix (variant C: symbolic evidence)",
    "c-concrete": "IEC 62304 Traceability Matrix (variant C: concrete evidence)",
}


# ---------------------------------------------------------------- evidence

def symbolic_record(manifest, bounds, code_location):
    """Realized record for the Sample A CrossHair capture."""
    if manifest["exit_code"] != 0:
        raise SystemExit(
            "symbolic capture does not report a clean pass "
            f"(exit_code={manifest['exit_code']}); refusing to bind"
        )
    return {
        "method": "crosshair",
        "strength": Strength.BOUNDED_CHECKED.value,
        "caveat": CAVEAT[Strength.BOUNDED_CHECKED],
        "code_location": code_location,
        "result_status": "no_counterexample",
        "bounds": bounds,
        "counterexample": None,
        "run_started_utc": manifest["started_utc"],
    }


def concrete_record(case):
    """Realized record for one T4-0 concrete run."""
    if not case["passed"]:
        raise SystemExit(
            f"concrete case {case['test_id']} did not pass; refusing to bind"
        )
    return {
        "method": "concrete_test",
        "strength": Strength.EXAMPLE_CHECKED.value,
        "caveat": CAVEAT[Strength.EXAMPLE_CHECKED],
        "code_location": case["function"],
        "test_id": case["test_id"],
        "result_status": "passed",
        "inputs": case["inputs"],
        "expected": case["expected"],
        "observed": case["observed"],
    }


def _intent(req, realized_strengths):
    """intent_ok plus a token-free note when intent is not realized."""
    intent_ok = req["intended_method"] in realized_strengths
    notes = []
    if not intent_ok:
        notes.append(
            "intended method per metadata not realized; realized: "
            + (", ".join(realized_strengths) if realized_strengths else "GAP")
        )
    return intent_ok, notes


def _header(variant_key, metadata, tool_versions):
    return {
        "artifact": _ARTIFACT_TITLES[variant_key],
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "tool_versions": tool_versions or {},
        "crosshair_bounds": metadata["toolchain"]["crosshair_bounds"],
    }


# ---------------------------------------------------------------- variant A

def build_matrix_variant_a(metadata, manifest, concrete_store, tool_versions=None):
    cases = {c["test_id"]: c for c in concrete_store["cases"]}
    bounds = metadata["toolchain"]["crosshair_bounds"]
    rows = []
    for req in metadata["requirements"]:
        records = []
        for ev in req.get("evidence", []):
            if ev["method"] == "crosshair":
                records.append(symbolic_record(manifest, bounds, req["implementation"]))
            elif ev["method"] == "concrete_test":
                records.append(concrete_record(cases[ev["test_id"]]))
            else:
                raise SystemExit(f"unknown evidence method: {ev['method']}")
        realized = [r["strength"] for r in records]
        intent_ok, notes = _intent(req, realized)
        if not records:
            notes.insert(0, "no evidence bound for this requirement")
        rows.append(
            {
                "requirement_id": req["id"],
                "requirement_text": req["text"].strip(),
                "code_location": req["implementation"],
                "evidence": records,
                "intent_ok": intent_ok,
                "notes": notes,
            }
        )
    matrix = _header("a", metadata, tool_versions)
    matrix["rows"] = rows
    return matrix, _markdown_variant_a(matrix)


def _markdown_variant_a(matrix):
    lines = _md_head(matrix)
    lines += [
        "| Requirement | Method | Strength | Result | Detail | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for row in matrix["rows"]:
        notes = "; ".join(row["notes"]) if row["notes"] else "—"
        for i, rec in enumerate(row["evidence"]):
            req_cell = f"**{row['requirement_id']}**" if i == 0 else "&nbsp;&nbsp;↳"
            lines.append(
                f"| {req_cell} | {rec['method']} | {rec['strength']} "
                f"| {rec['result_status']} | {_detail(rec)} | {notes if i == 0 else '—'} |"
            )
    lines += _md_caveats(_all_records_a(matrix)) + _md_notes(matrix["rows"])
    return "\n".join(lines)


def _all_records_a(matrix):
    return [rec for row in matrix["rows"] for rec in row["evidence"]]


# ---------------------------------------------------------------- variant B

def build_matrix_variant_b(metadata, manifest, concrete_store, tool_versions=None):
    cases = {c["test_id"]: c for c in concrete_store["cases"]}
    bounds = metadata["toolchain"]["crosshair_bounds"]
    rows = []
    for req in metadata["requirements"]:
        parent = req.get("parent_requirement")
        if parent is None:
            record = symbolic_record(manifest, bounds, req["implementation"])
        else:
            test_id = req["implementation"].split("::")[-1]
            record = concrete_record(cases[test_id])
        intent_ok, notes = _intent(req, [record["strength"]])
        rows.append(
            {
                "requirement_id": req["id"],
                "parent_requirement": parent,
                "requirement_text": req["text"].strip(),
                "code_location": req["implementation"],
                **{k: record[k] for k in ("method", "strength", "caveat", "result_status")},
                "bounds": record.get("bounds"),
                "counterexample": record.get("counterexample"),
                "inputs": record.get("inputs"),
                "expected": record.get("expected"),
                "observed": record.get("observed"),
                "intent_ok": intent_ok,
                "notes": notes,
            }
        )
    matrix = _header("b", metadata, tool_versions)
    matrix["rows"] = rows
    return matrix, _markdown_variant_b(matrix)


def _markdown_variant_b(matrix):
    lines = _md_head(matrix)
    lines += [
        "| Requirement | Parent | Method | Strength | Result | Detail | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    parents = [r for r in matrix["rows"] if r["parent_requirement"] is None]
    for parent in parents:
        for row in [parent] + [
            r for r in matrix["rows"] if r["parent_requirement"] == parent["requirement_id"]
        ]:
            is_shadow = row["parent_requirement"] is not None
            req_cell = (
                f"&nbsp;&nbsp;↳ {row['requirement_id']}"
                if is_shadow
                else f"**{row['requirement_id']}**"
            )
            notes = "; ".join(row["notes"]) if row["notes"] else "—"
            lines.append(
                f"| {req_cell} | {row['parent_requirement'] or '—'} | {row['method']} "
                f"| {row['strength']} | {row['result_status']} | {_detail(row)} | {notes} |"
            )
    lines += _md_caveats(matrix["rows"]) + _md_notes(matrix["rows"])
    return "\n".join(lines)


# ---------------------------------------------------------------- variant C

def build_matrix_variant_c(metadata, manifest, concrete_store, method, tool_versions=None):
    """Single renderer parametrised by method filter: 'crosshair' or
    'concrete_test'. Concrete evidence binds by the requirement_id carried in
    each concrete_results.json case (evidence is self-describing); symbolic
    evidence binds by implementation match, as in the base matrix."""
    bounds = metadata["toolchain"]["crosshair_bounds"]
    rows = []
    for req in metadata["requirements"]:
        if method == "crosshair":
            records = [symbolic_record(manifest, bounds, req["implementation"])]
        elif method == "concrete_test":
            records = [
                concrete_record(c)
                for c in concrete_store["cases"]
                if c["requirement_id"] == req["id"]
            ]
        else:
            raise SystemExit(f"unknown method filter: {method}")
        for record in records:
            intent_ok, notes = _intent(req, [record["strength"]])
            rows.append(
                {
                    "requirement_id": req["id"],
                    "requirement_text": req["text"].strip(),
                    "code_location": record["code_location"],
                    **{k: record[k] for k in ("method", "strength", "caveat", "result_status")},
                    "bounds": record.get("bounds"),
                    "counterexample": record.get("counterexample"),
                    "test_id": record.get("test_id"),
                    "inputs": record.get("inputs"),
                    "expected": record.get("expected"),
                    "observed": record.get("observed"),
                    "intent_ok": intent_ok,
                    "notes": notes,
                }
            )
    key = "c-symbolic" if method == "crosshair" else "c-concrete"
    matrix = _header(key, metadata, tool_versions)
    matrix["method_filter"] = method
    matrix["rows"] = rows
    return matrix, _markdown_variant_c(matrix)


def _markdown_variant_c(matrix):
    lines = _md_head(matrix)
    lines += [
        "| Requirement | Method | Strength | Result | Detail | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for row in matrix["rows"]:
        notes = "; ".join(row["notes"]) if row["notes"] else "—"
        lines.append(
            f"| {row['requirement_id']} | {row['method']} | {row['strength']} "
            f"| {row['result_status']} | {_detail(row)} | {notes} |"
        )
    lines += _md_caveats(matrix["rows"]) + _md_notes(matrix["rows"])
    return "\n".join(lines)


# ---------------------------------------------------------------- shared md

def _detail(rec):
    if rec["method"] == "crosshair":
        return f"bounds: {rec.get('bounds')}"
    return (
        f"test `{rec.get('test_id')}`; inputs {rec.get('inputs')}; "
        f"expected {rec.get('expected')}; observed {rec.get('observed')}"
    )


def _md_head(matrix):
    return [
        f"# {matrix['artifact']}",
        "",
        f"Generated (UTC): {matrix['generated_utc']}",
        f"Tool versions: {matrix['tool_versions']}",
        f"CrossHair bounds: {matrix['crosshair_bounds']}",
        "",
    ]


def _md_caveats(records):
    lines = ["", "## Caveats", ""]
    seen = []
    for rec in records:
        if rec["strength"] not in seen:
            seen.append(rec["strength"])
            lines.append(f"- **{rec['strength']}**: {rec['caveat'] if 'caveat' in rec else CAVEAT[Strength(rec['strength'])]}")
    return lines


def _md_notes(rows):
    lines = ["", "## Notes", ""]
    noted = False
    for row in rows:
        for note in row["notes"]:
            noted = True
            lines.append(f"- {row['requirement_id']}: {note}")
    if not noted:
        lines.append("- none")
    lines.append("")
    return lines
