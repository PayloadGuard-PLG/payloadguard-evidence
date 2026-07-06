"""Gate 2 CONFLICT rule, Type 1 (identity mismatch) — the first of the two
ratified sub-types (KNOWN_LIMITATIONS.md, Gate 2).

Type 1 fires when a top-down, metadata-authored binding and a bottom-up,
evidence-store-carried claim disagree about what physical target a
requirement's evidence actually is. Two shapes exist in this repo today:

  - Concrete evidence: metadata declares a binding two ways — variant A's
    per-requirement `evidence: [{method: concrete_test, test_id: ...}]`
    list, or variant B's shadow pseudo-requirements (`parent_requirement`
    + a test_id embedded as the implementation suffix). The bottom-up
    counterpart is `concrete_results.json`'s self-describing
    `requirement_id` field on each case. They must agree on which
    requirement owns the test.
  - Symbolic evidence: metadata declares `implementation` (e.g.
    "dosage.py::calculate_hourly_dose"); the crosshair run manifest
    records what file was actually invoked (`target`). The requirement's
    declared file must match the file the capture actually ran against.

Variant C's concrete binding declares no top-down test_id at all (Gate 4's
known asymmetry — evidence-store-carried only), so there is nothing to
cross-check on that side; that gap is exactly what Gate 4's option 3
(cross-checked dual-authorship) is meant to close once C also carries a
declared binding.

Type 2 (outcome mismatch — two claims agreeing on identity but
disagreeing on result) is NOT implemented here: it needs a
cross-manifest comparison mechanism that doesn't exist yet (see
KNOWN_LIMITATIONS.md, "What's left before Gate 2 can start building").
"""


def _declared_concrete_bindings(metadata):
    """Yield (declared_owner, test_id, declared_by) for every top-down
    concrete-test binding in metadata, across both shapes in use."""
    for req in metadata["requirements"]:
        parent = req.get("parent_requirement")
        if parent is not None:
            test_id = req["implementation"].split("::")[-1]
            yield parent, test_id, req["id"]
            continue
        for ev in req.get("evidence", []):
            if ev.get("method") == "concrete_test":
                yield req["id"], ev["test_id"], req["id"]


def concrete_binding_conflicts(metadata, concrete_store):
    """Type 1 check for concrete evidence: does the evidence-store's
    self-declared requirement_id agree with the metadata-declared owner?"""
    cases = {c["test_id"]: c for c in concrete_store["cases"]}
    conflicts = []
    for owner, test_id, declared_by in _declared_concrete_bindings(metadata):
        case = cases.get(test_id)
        if case is None:
            raise SystemExit(
                f"declared test_id {test_id!r} (via {declared_by}) not "
                "found in concrete_store; refusing to check a binding "
                "against evidence that doesn't exist"
            )
        if case["requirement_id"] != owner:
            conflicts.append(
                {
                    "type": "identity_mismatch",
                    "class": "concrete_binding",
                    "declared_owner": owner,
                    "declared_via": declared_by,
                    "test_id": test_id,
                    "evidence_store_owner": case["requirement_id"],
                }
            )
    return conflicts


def symbolic_binding_conflicts(metadata, manifest):
    """Type 1 check for symbolic evidence: does the requirement's declared
    implementation file agree with the file the crosshair capture manifest
    actually ran against? File-level only — crosshair's manifest records
    the file passed to `crosshair check`, not a per-method target, so this
    cannot detect a method-level mismatch within the same file."""
    conflicts = []
    manifest_file = manifest["target"]
    for req in metadata["requirements"]:
        if req.get("parent_requirement") is not None:
            continue  # shadow rows bind to concrete evidence, not crosshair
        impl = req.get("implementation")
        if impl is None:
            continue  # not a code-verified requirement (e.g. a threat entry)
        impl_file = impl.split("::")[0]
        if impl_file != manifest_file:
            conflicts.append(
                {
                    "type": "identity_mismatch",
                    "class": "symbolic_binding",
                    "requirement_id": req["id"],
                    "declared_target_file": impl_file,
                    "manifest_target_file": manifest_file,
                }
            )
    return conflicts


def run_conflict_gate(metadata, concrete_store, manifest):
    """Type 1 CONFLICT gate. Raises AssertionError on any identity
    mismatch; returns a small summary dict on success. Tier 1
    (REVIEW_PROTOCOL.md): a real conflict stops generation, it is never
    rendered as a soft warning or fixed by editing a generated artifact."""
    conflicts = concrete_binding_conflicts(
        metadata, concrete_store
    ) + symbolic_binding_conflicts(metadata, manifest)
    if conflicts:
        raise AssertionError(
            f"CONFLICT gate failed (Type 1, identity mismatch): {conflicts}"
        )
    checked = sum(1 for _ in _declared_concrete_bindings(metadata)) + sum(
        1
        for req in metadata["requirements"]
        if req.get("parent_requirement") is None and req.get("implementation")
    )
    return {"bindings_checked": checked, "conflicts": 0}
