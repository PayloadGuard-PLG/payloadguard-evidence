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

  - Dafny evidence (2026-07-07, Gate 2/C2-C4 wiring; extended to variants
    A/B 2026-07-07): metadata declares a dafny binding two ways, mirroring
    concrete evidence's own A/B split — variant A/C's per-requirement
    `evidence: [{method: dafny, spec_target: "dosage.dfy", dafny_method:
    "CalculateHourlyDose"}]` list, or variant B's shadow pseudo-
    requirements (`parent_requirement` + an `implementation` pointing at
    a `.dfy` file, e.g. `dosage.dfy::CalculateHourlyDose` — distinguished
    from a concrete shadow by that file extension, not a separate
    declared field). The bottom-up counterpart is a `dafny_store` dict
    (assembled by the calling script from a real committed Dafny capture,
    keyed by `"{spec_target}::{dafny_method}"`) whose manifest records
    what file was actually verified. `dafny_binding_conflicts` is a no-op
    (returns no conflicts) when `dafny_store is None` — a caller that
    never intends to bind dafny evidence at all must not be penalized for
    metadata that declares it.

Type 2 (outcome mismatch) is implemented below: two manifests that claim
the identical verification act (same tool, same target, same
per_condition_timeout) but report different outcomes (exit_code). No
committed manifest in this repository currently shares an identity with
another — each targets a distinct file (Sample A, Sample B, the naive-
widening exhibit, the overflow probe) — so this check is real but has
nothing to compare against in today's honest data; see
tests/test_conflict_check.py for a synthetic positive case, and Gate 3's
documented CrossHair model-fidelity non-determinism for why this check
exists at all (the same invocation really can land differently).
"""


def _declared_concrete_bindings(metadata):
    """Yield (declared_owner, test_id, declared_by) for every top-down
    concrete-test binding in metadata, across both shapes in use.
    Shadow rows whose implementation targets a .dfy file are dafny
    shadows, not concrete ones (see _declared_dafny_bindings) - skipped
    here rather than mistakenly treated as a concrete test_id."""
    for req in metadata["requirements"]:
        parent = req.get("parent_requirement")
        if parent is not None:
            impl_file = req["implementation"].split("::")[0]
            if impl_file.endswith(".dfy"):
                continue
            test_id = req["implementation"].split("::")[-1]
            yield parent, test_id, req["id"]
            continue
        for ev in req.get("evidence", []):
            if ev.get("method") == "concrete_test":
                yield req["id"], ev["test_id"], req["id"]


def _declared_dafny_bindings(metadata):
    """Yield (declared_owner, spec_target, dafny_method, declared_by) for
    every top-down dafny binding in metadata, across both shapes in use:
    variant A/C's per-requirement `evidence: [{method: dafny, ...}]` list,
    and variant B's shadow pseudo-requirements (implementation pointing
    at a .dfy file)."""
    for req in metadata["requirements"]:
        parent = req.get("parent_requirement")
        if parent is not None:
            impl_file, _, impl_method = req["implementation"].partition("::")
            if impl_file.endswith(".dfy"):
                yield parent, impl_file, impl_method, req["id"]
            continue
        for ev in req.get("evidence", []):
            if ev.get("method") == "dafny":
                yield req["id"], ev["spec_target"], ev["dafny_method"], req["id"]


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
    cannot detect a method-level mismatch within the same file.

    `manifest` may be `None` (a metadata file that declares no crosshair
    evidence at all — the first Dafny-only worked examples, 2026-07):
    callers must skip this check entirely in that case, mirroring
    `dafny_binding_conflicts`' own `dafny_store is None` no-op, rather
    than call in here and hit an unconditional `manifest["target"]`."""
    conflicts = []
    manifest_file = manifest["target"]
    for req in metadata["requirements"]:
        if req.get("parent_requirement") is not None:
            continue  # shadow rows bind to concrete evidence, not crosshair
        impl = req.get("implementation")
        if impl is None:
            continue  # not a code-verified requirement (e.g. a threat entry)
        impl_file = impl.split("::")[0]
        if impl_file.endswith(".dfy"):
            continue  # dafny-backed requirement, not crosshair-checkable —
            # mirrors _declared_concrete_bindings' own .dfy skip above
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


def dafny_binding_conflicts(metadata, dafny_store):
    """Type 1 check for Dafny evidence: does the requirement's declared
    spec_target agree with the file the captured Dafny manifest actually
    verified? Covers both declaration shapes via _declared_dafny_bindings
    (variant A/C's `evidence` list and variant B's .dfy-suffixed shadow
    rows), the same dual-shape pattern concrete evidence already uses.
    `dafny_store` keys are `"{spec_target}::{dafny_method}"`; a declared
    key absent from the store is itself a conflict (the binding points at
    evidence that doesn't exist). Deliberately a no-op when `dafny_store
    is None` (not merely falsy/empty) — that means the caller isn't
    binding dafny evidence in this call at all, as opposed to genuinely
    having zero captures to check."""
    if dafny_store is None:
        return []
    conflicts = []
    for owner, spec_target, dafny_method, declared_by in _declared_dafny_bindings(metadata):
        key = f"{spec_target}::{dafny_method}"
        capture = dafny_store.get(key)
        if capture is None:
            conflicts.append(
                {
                    "type": "identity_mismatch",
                    "class": "dafny_binding",
                    "declared_owner": owner,
                    "declared_via": declared_by,
                    "declared_key": key,
                    "evidence_store_owner": None,
                }
            )
            continue
        manifest_target = capture["manifest"].get("target")
        if manifest_target != spec_target:
            conflicts.append(
                {
                    "type": "identity_mismatch",
                    "class": "dafny_binding",
                    "declared_owner": owner,
                    "declared_via": declared_by,
                    "declared_target_file": spec_target,
                    "manifest_target_file": manifest_target,
                }
            )
    return conflicts


def _manifest_identity(manifest):
    """Identity key for Type 2: two manifests are claims about the SAME
    verification act iff they agree on tool, target, and the enforced
    timeout bound. Deliberately excludes the raw command list (which
    embeds an environment-specific absolute path) and started_utc (which
    is never expected to match)."""
    bounds = manifest.get("effective_bounds", {})
    return (
        manifest.get("tool"),
        manifest.get("target"),
        bounds.get("per_condition_timeout_s"),
    )


def _manifest_outcome(manifest):
    """The reported result of a verification act, for Type 2 comparison."""
    return manifest.get("exit_code")


def outcome_conflicts(manifests):
    """Type 2 CONFLICT check: group manifests by identity; any group
    reporting more than one distinct outcome is a conflict. `manifests` is
    a dict of {name: manifest_dict} so conflicts can name their source."""
    by_identity = {}
    for name, manifest in manifests.items():
        by_identity.setdefault(_manifest_identity(manifest), []).append(name)
    conflicts = []
    for identity, names in by_identity.items():
        outcomes = {name: _manifest_outcome(manifests[name]) for name in names}
        if len(set(outcomes.values())) > 1:
            conflicts.append(
                {
                    "type": "outcome_mismatch",
                    "class": "evidence_outcome",
                    "identity": identity,
                    "outcomes": outcomes,
                }
            )
    return conflicts


def run_outcome_gate(manifests):
    """Type 2 CONFLICT gate. Raises AssertionError on any outcome
    mismatch; returns a small summary dict on success."""
    conflicts = outcome_conflicts(manifests)
    if conflicts:
        raise AssertionError(
            f"CONFLICT gate failed (Type 2, outcome mismatch): {conflicts}"
        )
    distinct = {_manifest_identity(m) for m in manifests.values()}
    return {
        "manifests_checked": len(manifests),
        "distinct_identities": len(distinct),
        "conflicts": 0,
    }


def run_conflict_gate(metadata, concrete_store, manifest, dafny_store=None):
    """Type 1 CONFLICT gate. Raises AssertionError on any identity
    mismatch; returns a small summary dict on success. Tier 1
    (REVIEW_PROTOCOL.md): a real conflict stops generation, it is never
    rendered as a soft warning or fixed by editing a generated artifact.
    `dafny_store` defaults to None (skips the dafny check entirely) for
    backward compatibility with every call site that predates Gate 2/C2-
    C4 wiring (the frozen base matrix, variants A/B, and variant C's own
    symbolic/concrete sub-views, none of which bind dafny evidence).
    `manifest` may likewise be None (2026-07, the first Dafny-only worked
    examples — no crosshair evidence declared anywhere in metadata),
    skipping the symbolic check the same way — a caller that never
    intends to bind crosshair evidence at all must not be penalized for
    metadata that declares none, mirroring dafny_store's own precedent
    exactly rather than inventing a new convention."""
    conflicts = (
        concrete_binding_conflicts(metadata, concrete_store)
        + (symbolic_binding_conflicts(metadata, manifest) if manifest is not None else [])
        + dafny_binding_conflicts(metadata, dafny_store)
    )
    if conflicts:
        raise AssertionError(
            f"CONFLICT gate failed (Type 1, identity mismatch): {conflicts}"
        )
    checked = (
        sum(1 for _ in _declared_concrete_bindings(metadata))
        + sum(
            1
            for req in metadata["requirements"]
            if req.get("parent_requirement") is None and req.get("implementation")
        )
        + (sum(1 for _ in _declared_dafny_bindings(metadata)) if dafny_store is not None else 0)
    )
    return {"bindings_checked": checked, "conflicts": 0}
