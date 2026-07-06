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
  - intent_ok is requirement-scoped and derived ONCE at the model level
    (derive_intent, ruling R1); projections carry it read-only.
  - Intent-mismatch notes inline intended_method verbatim (ruling R2:
    quoting authored metadata is fidelity, not a violation); the structural
    rule enforced by assert_no_realized_proven() is that PROVEN never
    appears as a REALIZED strength in any record or rendered cell.
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


def derive_intent(metadata, records_by_requirement):
    """R1 bind-time derivation invariant: intent_ok is requirement-scoped and
    computed exactly ONCE here, at the model level — true iff ANY evidence
    record bound to the requirement realizes the intended strength. Every
    variant matrix (including method-filtered views) carries these values
    read-only and never re-derives them. Shadow pseudo-requirements (variant
    B) project their parent's value."""
    intent = {}
    for req in metadata["requirements"]:
        if req.get("parent_requirement") is not None:
            continue
        realized = []
        by_method = {}
        for rec in records_by_requirement.get(req["id"], []):
            if rec["strength"] not in realized:
                realized.append(rec["strength"])
            per = by_method.setdefault(rec["method"], [])
            if rec["strength"] not in per:
                per.append(rec["strength"])
        intent_ok = req["intended_method"] in realized
        notes = []
        if not intent_ok:
            # R2: intended_method is inlined verbatim (quoting authored
            # metadata is required for fidelity). The structural rule is
            # enforced separately: no REALIZED strength may be PROVEN — see
            # assert_no_realized_proven().
            notes.append(
                f"intended {req['intended_method']}, realized "
                + (", ".join(realized) if realized else "GAP")
            )
        intent[req["id"]] = {
            "intent_ok": intent_ok,
            "notes": notes,
            "intended": req["intended_method"],
            "by_method": by_method,
        }
    return intent


def _display_text(req):
    """Gate 1 remediation, Item 1: when a requirement declares a
    kernel_scope, the bound evidence supports the kernel_scope claim, not
    the bare requirement text — evidence rows reference it explicitly."""
    if "kernel_scope" in req:
        return "[kernel_scope] " + " ".join(req["kernel_scope"].split())
    return req["text"].strip()


def scope_gap_record(req):
    """Explicit GAP for a declared-but-unevidenced scope (system_scope).
    Rendered in every view — a named gap, never a silent omission. A GAP is
    the absence of evidence: it is NOT a fact
    (evidence.reconcile.normalize_facts excludes GAP strength), and it does
    not participate in intent derivation."""
    if "system_scope" not in req:
        return None
    return {
        "method": None,
        "strength": Strength.GAP.value,
        "caveat": CAVEAT[Strength.GAP],
        "scope": "system_scope",
        "scope_text": " ".join(req["system_scope"].split()),
        "code_location": None,
        "result_status": None,
        "note": (
            "system_scope declared but not evidenced at this phase; "
            "deferred to integration testing (explicit GAP, not omission)"
        ),
    }


def _view_notes(intent_entry, method):
    """Gate 1 remediation, Item 2(a): a single-evidence-type view's notes
    describe only that evidence type's contribution. The requirement-scoped
    intent_ok VALUE is never re-derived (R1) — only the note text is scoped
    to the rendering view."""
    if intent_entry["intent_ok"]:
        return []
    here = intent_entry["by_method"].get(method, [])
    return [
        f"intended {intent_entry['intended']}; realized in this view: "
        + (", ".join(here) if here else "none")
        + " (requirement-scoped intent evaluated across all evidence per R1)"
    ]


def assert_no_realized_proven(matrix):
    """R2 structural rule: PROVEN must never appear as a realized/assigned
    strength in any evidence record or rendered strength cell. (It MAY appear
    inside intent-mismatch notes quoting authored metadata.) Called by every
    variant builder before returning; generation fails hard on violation."""
    for row in matrix["rows"]:
        for rec in row.get("evidence", []):
            if rec["strength"] == "PROVEN":
                raise AssertionError(
                    "structural PROVEN check failed: evidence record for "
                    f"{row['requirement_id']} carries realized strength PROVEN"
                )
        if row.get("strength") == "PROVEN":
            raise AssertionError(
                "structural PROVEN check failed: row for "
                f"{row['requirement_id']} carries realized strength PROVEN"
            )


def derive_bounds_block(metadata, manifest):
    """Turn 2.0 (B1): declared bounds are the intended envelope authored in
    metadata; effective bounds are what the capture invocation actually
    enforced, read from the run manifest (single source of truth). Derived
    once at the model level; every view carries the block read-only."""
    if "effective_bounds" not in manifest:
        raise SystemExit(
            "capture manifest lacks effective_bounds; re-run the Turn 2.0 "
            "capture runners before generating matrices"
        )
    effective = dict(manifest["effective_bounds"])
    note = effective.pop("enforcement_note", "")
    return {
        "declared": metadata["toolchain"]["crosshair_bounds"],
        "effective": effective,
        "enforcement_note": note,
    }


def _header(variant_key, metadata, tool_versions, bounds_block):
    return {
        "artifact": _ARTIFACT_TITLES[variant_key],
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "tool_versions": tool_versions or {},
        "crosshair_bounds": metadata["toolchain"]["crosshair_bounds"],
        "bounds": bounds_block,
    }


# ---------------------------------------------------------------- variant A

def build_matrix_variant_a(metadata, manifest, concrete_store, tool_versions=None):
    cases = {c["test_id"]: c for c in concrete_store["cases"]}
    bounds = metadata["toolchain"]["crosshair_bounds"]
    records_by_req = {}
    for req in metadata["requirements"]:
        records = []
        for ev in req.get("evidence", []):
            if ev["method"] == "crosshair":
                records.append(symbolic_record(manifest, bounds, req["implementation"]))
            elif ev["method"] == "concrete_test":
                records.append(concrete_record(cases[ev["test_id"]]))
            else:
                raise SystemExit(f"unknown evidence method: {ev['method']}")
        records_by_req[req["id"]] = records
    intent = derive_intent(metadata, records_by_req)
    rows = []
    for req in metadata["requirements"]:
        records = records_by_req[req["id"]]
        notes = list(intent[req["id"]]["notes"])
        if not records:
            notes.insert(0, "no evidence bound for this requirement")
        gap = scope_gap_record(req)
        if gap:
            records = records + [gap]
            notes.append(gap["note"])
        rows.append(
            {
                "requirement_id": req["id"],
                "requirement_text": _display_text(req),
                "code_location": req["implementation"],
                "evidence": records,
                "intent_ok": intent[req["id"]]["intent_ok"],
                "notes": notes,
            }
        )
    matrix = _header("a", metadata, tool_versions, derive_bounds_block(metadata, manifest))
    matrix["rows"] = rows
    assert_no_realized_proven(matrix)
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
                f"| {req_cell} | {rec['method'] or '—'} | {rec['strength']} "
                f"| {rec['result_status'] or '—'} | {_detail(rec)} | {notes if i == 0 else '—'} |"
            )
    lines += _md_caveats(_all_records_a(matrix)) + _md_notes(matrix["rows"])
    return "\n".join(lines)


def _all_records_a(matrix):
    return [rec for row in matrix["rows"] for rec in row["evidence"]]


# ---------------------------------------------------------------- variant B

def build_matrix_variant_b(metadata, manifest, concrete_store, tool_versions=None):
    cases = {c["test_id"]: c for c in concrete_store["cases"]}
    bounds = metadata["toolchain"]["crosshair_bounds"]
    bound_record = {}
    records_by_req = {}
    for req in metadata["requirements"]:
        parent = req.get("parent_requirement")
        if parent is None:
            record = symbolic_record(manifest, bounds, req["implementation"])
            records_by_req.setdefault(req["id"], []).append(record)
        else:
            test_id = req["implementation"].split("::")[-1]
            record = concrete_record(cases[test_id])
            records_by_req.setdefault(parent, []).append(record)
        bound_record[req["id"]] = record
    intent = derive_intent(metadata, records_by_req)
    rows = []
    for req in metadata["requirements"]:
        parent = req.get("parent_requirement")
        record = bound_record[req["id"]]
        # R1: rows project the requirement-scoped value read-only; shadow rows
        # carry their parent's intent_ok, and the requirement-scoped notes are
        # displayed on the parent row only.
        scope = intent[parent or req["id"]]
        intent_ok = scope["intent_ok"]
        notes = list(scope["notes"]) if parent is None else []
        req_text = req["text"].strip() if parent else _display_text(req)
        rows.append(
            {
                "requirement_id": req["id"],
                "parent_requirement": parent,
                "requirement_text": req_text,
                "code_location": req["implementation"],
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
    for req in metadata["requirements"]:
        if req.get("parent_requirement") is not None:
            continue
        gap = scope_gap_record(req)
        if gap:
            rows.append(_gap_row(req, gap, intent[req["id"]]["intent_ok"]))
    matrix = _header("b", metadata, tool_versions, derive_bounds_block(metadata, manifest))
    matrix["rows"] = rows
    assert_no_realized_proven(matrix)
    return matrix, _markdown_variant_b(matrix)


def _markdown_variant_b(matrix):
    lines = _md_head(matrix)
    lines += [
        "| Requirement | Parent | Method | Strength | Result | Detail | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    # Evidence-bearing parents anchor the groups; scope-GAP rows (same
    # requirement_id, strength GAP) render inside their requirement's group
    # rather than anchoring a duplicate one.
    parents = [
        r
        for r in matrix["rows"]
        if r["parent_requirement"] is None and r["strength"] != Strength.GAP.value
    ]
    for parent in parents:
        group = (
            [parent]
            + [r for r in matrix["rows"] if r["parent_requirement"] == parent["requirement_id"]]
            + [
                r
                for r in matrix["rows"]
                if r["parent_requirement"] is None
                and r["strength"] == Strength.GAP.value
                and r["requirement_id"] == parent["requirement_id"]
            ]
        )
        for row in group:
            is_shadow = row["parent_requirement"] is not None
            is_gap = row["strength"] == Strength.GAP.value
            if is_shadow:
                req_cell = f"&nbsp;&nbsp;↳ {row['requirement_id']}"
            elif is_gap:
                req_cell = f"&nbsp;&nbsp;↳ {row['requirement_id']} [system_scope]"
            else:
                req_cell = f"**{row['requirement_id']}**"
            notes = "; ".join(row["notes"]) if row["notes"] else "—"
            lines.append(
                f"| {req_cell} | {row['parent_requirement'] or '—'} | {row['method'] or '—'} "
                f"| {row['strength']} | {row['result_status'] or '—'} | {_detail(row)} | {notes} |"
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
    # R1: the full evidence model (BOTH methods) is assembled first and intent
    # is derived once at the model level; the method filter below only selects
    # which records are projected into this artifact. Filtered views carry the
    # requirement-scoped intent_ok read-only and never re-derive it.
    records_by_req = {}
    for req in metadata["requirements"]:
        records_by_req[req["id"]] = [
            symbolic_record(manifest, bounds, req["implementation"])
        ] + [
            concrete_record(c)
            for c in concrete_store["cases"]
            if c["requirement_id"] == req["id"]
        ]
    intent = derive_intent(metadata, records_by_req)
    rows = []
    for req in metadata["requirements"]:
        if method == "crosshair":
            records = [r for r in records_by_req[req["id"]] if r["method"] == "crosshair"]
        elif method == "concrete_test":
            records = [r for r in records_by_req[req["id"]] if r["method"] == "concrete_test"]
        else:
            raise SystemExit(f"unknown method filter: {method}")
        for record in records:
            intent_ok = intent[req["id"]]["intent_ok"]
            notes = _view_notes(intent[req["id"]], method)
            rows.append(
                {
                    "requirement_id": req["id"],
                    "requirement_text": _display_text(req),
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
    # Scope gaps are method-agnostic (they mark the ABSENCE of evidence of
    # any type), so both filtered views carry them — a deferred scope must
    # be visible no matter which artifact a reviewer opens.
    for req in metadata["requirements"]:
        gap = scope_gap_record(req)
        if gap:
            rows.append(_gap_row(req, gap, intent[req["id"]]["intent_ok"]))
    key = "c-symbolic" if method == "crosshair" else "c-concrete"
    matrix = _header(key, metadata, tool_versions, derive_bounds_block(metadata, manifest))
    matrix["method_filter"] = method
    matrix["rows"] = rows
    assert_no_realized_proven(matrix)
    return matrix, _markdown_variant_c(matrix)


def _markdown_variant_c(matrix):
    lines = _md_head(matrix)
    lines += [
        "| Requirement | Method | Strength | Result | Detail | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for row in matrix["rows"]:
        notes = "; ".join(row["notes"]) if row["notes"] else "—"
        req_cell = row["requirement_id"]
        if row["strength"] == Strength.GAP.value:
            req_cell += " [system_scope]"
        lines.append(
            f"| {req_cell} | {row['method'] or '—'} | {row['strength']} "
            f"| {row['result_status'] or '—'} | {_detail(row)} | {notes} |"
        )
    lines += _md_caveats(matrix["rows"]) + _md_notes(matrix["rows"])
    return "\n".join(lines)


# ---------------------------------------------------------------- shared md

def _gap_row(req, gap, intent_ok):
    """Row shape for a declared-but-unevidenced scope, shared by B and C."""
    return {
        "requirement_id": req["id"],
        "parent_requirement": None,
        "requirement_text": "[system_scope — GAP] " + gap["scope_text"],
        "code_location": None,
        "method": None,
        "strength": gap["strength"],
        "caveat": gap["caveat"],
        "result_status": None,
        "bounds": None,
        "counterexample": None,
        "test_id": None,
        "inputs": None,
        "expected": None,
        "observed": None,
        "scope": gap["scope"],
        "intent_ok": intent_ok,
        "notes": [gap["note"]],
    }


def _detail(rec):
    if rec.get("strength") == Strength.GAP.value:
        return f"deferred scope `{rec.get('scope')}` — no evidence at this phase"
    if rec["method"] == "crosshair":
        return f"bounds: {rec.get('bounds')}"
    return (
        f"test `{rec.get('test_id')}`; inputs {rec.get('inputs')}; "
        f"expected {rec.get('expected')}; observed {rec.get('observed')}"
    )


def _md_head(matrix):
    bounds = matrix["bounds"]
    return [
        f"# {matrix['artifact']}",
        "",
        f"Generated (UTC): {matrix['generated_utc']}",
        f"Tool versions: {matrix['tool_versions']}",
        f"Declared bounds (intended envelope): {bounds['declared']}",
        f"Effective bounds (demonstrated by capture): {bounds['effective']}",
        f"Enforcement note: {bounds['enforcement_note']}",
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
    # Gate 1 remediation, Item 2(b): the aggregate section de-duplicates by
    # (requirement, note) — one line per unique requirement-level note, not
    # one per table row.
    lines = ["", "## Notes", ""]
    seen = []
    for row in rows:
        for note in row["notes"]:
            key = (row["requirement_id"], note)
            if key not in seen:
                seen.append(key)
                lines.append(f"- {row['requirement_id']}: {note}")
    if not seen:
        lines.append("- none")
    lines.append("")
    return lines


# =============================================================================
# Gate 2: vocabulary-agnostic binder
#
# build_matrix() below is now the AUTHORITATIVE entry point: as of
# 2026-07-06, generate_matrix_a.py / _b.py / _c.py all call it instead of
# build_matrix_variant_a/b/c directly. Those three functions are literal
# extractions into named, reusable pieces ("binder" = record-assembly,
# "shape" = row-rendering), dispatched through one declarative table
# (_VARIANT_SPECS) and one entry point instead of three separate top-level
# functions.
#
# Binding strategy (how records_by_req gets populated) and row shape (how
# records_by_req renders into matrix rows) are the two real axes of variation
# across A/B/C; this split is what lets a future fifth shape reuse an
# existing strategy or shape instead of requiring a fourth whole function.
#
# Correctness discipline: this was a refactor of already-reviewed logic, not
# new logic. tests/test_binder_equivalence.py proves build_matrix() produces
# BYTE-IDENTICAL output (generated_utc aside) to build_matrix_variant_a/b/c
# for all four variant keys, over the real committed inputs - that proof
# held before the cutover above and continues to be enforced by the suite.
#
# build_matrix_variant_a/b/c (above this section) are INTENTIONALLY KEPT,
# unused by any generator now, as a fallback: if a problem with build_matrix
# ever surfaces, each generator script's import + call can be reverted to
# the corresponding build_matrix_variant_* function in one line, or this
# cutover commit can be git-reverted outright. They are deleted only in a
# later, separate cleanup step once this cutover has proven stable - not in
# the same step as the cutover itself.
# =============================================================================


def _bind_declared(metadata, manifest, concrete_store, bounds):
    """Variant A's binding strategy: metadata's per-requirement `evidence`
    list is authoritative and drives which records get assembled."""
    cases = {c["test_id"]: c for c in concrete_store["cases"]}
    records_by_req = {}
    for req in metadata["requirements"]:
        records = []
        for ev in req.get("evidence", []):
            if ev["method"] == "crosshair":
                records.append(symbolic_record(manifest, bounds, req["implementation"]))
            elif ev["method"] == "concrete_test":
                records.append(concrete_record(cases[ev["test_id"]]))
            else:
                raise SystemExit(f"unknown evidence method: {ev['method']}")
        records_by_req[req["id"]] = records
    return records_by_req


def _shape_evidence_array(metadata, records_by_req, intent):
    """Variant A's row shape: one row per requirement, evidence as a list."""
    rows = []
    for req in metadata["requirements"]:
        records = records_by_req[req["id"]]
        notes = list(intent[req["id"]]["notes"])
        if not records:
            notes.insert(0, "no evidence bound for this requirement")
        gap = scope_gap_record(req)
        if gap:
            records = records + [gap]
            notes.append(gap["note"])
        rows.append(
            {
                "requirement_id": req["id"],
                "requirement_text": _display_text(req),
                "code_location": req["implementation"],
                "evidence": records,
                "intent_ok": intent[req["id"]]["intent_ok"],
                "notes": notes,
            }
        )
    return rows


def _bind_shadow(metadata, manifest, concrete_store, bounds):
    """Variant B's binding strategy: non-shadow requirements get an implicit
    crosshair record; shadow pseudo-requirements (parent_requirement set)
    get a concrete record via a test_id embedded as the implementation
    suffix, attributed to the parent. Returns (records_by_req, bound_record)
    - bound_record carries one record per METADATA entry (shadow or not),
    needed by the flattened-shadow shape to render one row per entry."""
    cases = {c["test_id"]: c for c in concrete_store["cases"]}
    bound_record = {}
    records_by_req = {}
    for req in metadata["requirements"]:
        parent = req.get("parent_requirement")
        if parent is None:
            record = symbolic_record(manifest, bounds, req["implementation"])
            records_by_req.setdefault(req["id"], []).append(record)
        else:
            test_id = req["implementation"].split("::")[-1]
            record = concrete_record(cases[test_id])
            records_by_req.setdefault(parent, []).append(record)
        bound_record[req["id"]] = record
    return records_by_req, bound_record


def _shape_flattened_shadow(metadata, bound_record, intent):
    """Variant B's row shape: one row per metadata entry; shadow rows carry
    parent_requirement and project their parent's intent_ok read-only (R1)."""
    rows = []
    for req in metadata["requirements"]:
        parent = req.get("parent_requirement")
        record = bound_record[req["id"]]
        scope = intent[parent or req["id"]]
        intent_ok = scope["intent_ok"]
        notes = list(scope["notes"]) if parent is None else []
        req_text = req["text"].strip() if parent else _display_text(req)
        rows.append(
            {
                "requirement_id": req["id"],
                "parent_requirement": parent,
                "requirement_text": req_text,
                "code_location": req["implementation"],
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
    for req in metadata["requirements"]:
        if req.get("parent_requirement") is not None:
            continue
        gap = scope_gap_record(req)
        if gap:
            rows.append(_gap_row(req, gap, intent[req["id"]]["intent_ok"]))
    return rows


def _bind_self_describing(metadata, manifest, concrete_store, bounds):
    """Variant C's binding strategy: every requirement gets an implicit
    crosshair record unconditionally, plus every concrete_results.json case
    whose own requirement_id names it (evidence-store-carried, self
    describing - Gate 4's known asymmetry: no metadata declaration drives
    this binding, even though metadata.c.yaml now ALSO carries an `evidence`
    list for Type 1 cross-checking only, per Gate 4 option 3)."""
    records_by_req = {}
    for req in metadata["requirements"]:
        records_by_req[req["id"]] = [
            symbolic_record(manifest, bounds, req["implementation"])
        ] + [
            concrete_record(c)
            for c in concrete_store["cases"]
            if c["requirement_id"] == req["id"]
        ]
    return records_by_req


def _shape_method_partitioned(metadata, records_by_req, intent, method):
    """Variant C's row shape: one row per record, filtered by method into
    one of two independent artifacts; scope-GAP rows are method-agnostic
    and appear in both."""
    rows = []
    for req in metadata["requirements"]:
        if method == "crosshair":
            records = [r for r in records_by_req[req["id"]] if r["method"] == "crosshair"]
        elif method == "concrete_test":
            records = [r for r in records_by_req[req["id"]] if r["method"] == "concrete_test"]
        else:
            raise SystemExit(f"unknown method filter: {method}")
        for record in records:
            intent_ok = intent[req["id"]]["intent_ok"]
            notes = _view_notes(intent[req["id"]], method)
            rows.append(
                {
                    "requirement_id": req["id"],
                    "requirement_text": _display_text(req),
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
    for req in metadata["requirements"]:
        gap = scope_gap_record(req)
        if gap:
            rows.append(_gap_row(req, gap, intent[req["id"]]["intent_ok"]))
    return rows


_VARIANT_SPECS = {
    "a": {"binder": "declared", "shape": "evidence_array"},
    "b": {"binder": "shadow", "shape": "flattened_shadow"},
    "c-symbolic": {"binder": "self_describing", "shape": "method_partitioned", "method": "crosshair"},
    "c-concrete": {"binder": "self_describing", "shape": "method_partitioned", "method": "concrete_test"},
}

_MARKDOWN_RENDERERS = {
    "a": _markdown_variant_a,
    "b": _markdown_variant_b,
    "c-symbolic": _markdown_variant_c,
    "c-concrete": _markdown_variant_c,
}


def build_matrix(variant_key, metadata, manifest, concrete_store, tool_versions=None):
    """Vocabulary-agnostic entry point: one implementation driving all four
    schema-variant shapes via a declarative binder+shape dispatch, instead of
    a separate top-level function per variant. See the module-level note
    above this section for the correctness discipline this was built under."""
    spec = _VARIANT_SPECS[variant_key]
    bounds = metadata["toolchain"]["crosshair_bounds"]

    if spec["binder"] == "declared":
        records_by_req = _bind_declared(metadata, manifest, concrete_store, bounds)
        intent = derive_intent(metadata, records_by_req)
        rows = _shape_evidence_array(metadata, records_by_req, intent)
    elif spec["binder"] == "shadow":
        records_by_req, bound_record = _bind_shadow(metadata, manifest, concrete_store, bounds)
        intent = derive_intent(metadata, records_by_req)
        rows = _shape_flattened_shadow(metadata, bound_record, intent)
    elif spec["binder"] == "self_describing":
        records_by_req = _bind_self_describing(metadata, manifest, concrete_store, bounds)
        intent = derive_intent(metadata, records_by_req)
        rows = _shape_method_partitioned(metadata, records_by_req, intent, spec["method"])
    else:
        raise SystemExit(f"unknown binder strategy: {spec['binder']}")

    matrix = _header(variant_key, metadata, tool_versions, derive_bounds_block(metadata, manifest))
    if "method" in spec:
        matrix["method_filter"] = spec["method"]
    matrix["rows"] = rows
    assert_no_realized_proven(matrix)
    return matrix, _MARKDOWN_RENDERERS[variant_key](matrix)
