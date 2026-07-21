"""Tier 3 authoring migration: tests for evidence/contract_attestation.py -
the contract-ratification artifact (the human half of Component F),
template v2 (defeater-based).

The module builds the ratification TEMPLATE and mechanically checks its
structure; it never performs the ratification (drafter != checker). These
tests pin: the four committed v2 artifacts match the generator (byte-pin
while unsigned - the drift pin deliberately DOES NOT apply to a signed
artifact, whose designed successor guards are the structural invariants);
completion semantics (Wrong-if/Gap-if/Adopted all PENDING-gated, folded-in
Component D review required); the tamper cases (stale hash, gutted frozen
content, gutted production fields, gutted requirement text); and the
auto-assembly corrections verified against the real committed matrices
(evidence-level code_location matching, per-declaration definitional
banners)."""

import pathlib

import pytest

from evidence.contract_attestation import (
    _is_definitional,
    _matched_rows,
    build_attestation,
    check_attestation,
    check_example,
    contract_hash,
    load_citations,
    load_matrix,
)
from evidence.frozen_contract import build_frozen_contract, load_manifest
from evidence.source_anchored_review import PENDING

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
EXAMPLES = REPO_ROOT / "examples"

# (spec .dfy, folded-in Component D review, committed attestation artifact)
COMMITTED = {
    "dosage_calculator": (
        "dosage.dfy", "source_anchored_review_dosage.md", "contract_attestation_dosage.md"),
    "renal_adjustment": (
        "renal_adjustment.dfy", "source_anchored_review_renal.md", "contract_attestation_renal.md"),
    "aeb_kernel": (
        "aeb_kernel.dfy", "source_anchored_review_aeb.md", "contract_attestation_aeb.md"),
    "drug_interaction_checker": (
        "drug_interaction_checker.dfy", "source_anchored_review_ddi.md", "contract_attestation_ddi.md"),
}


def _paths(example):
    spec, review, attestation = COMMITTED[example]
    d = EXAMPLES / example
    return spec, d / "frozen_contract.yaml", d / review, d / attestation


def _data(example):
    """(spec, manifest, review_path, attestation_path, matrix, citations)"""
    spec, manifest_path, review_path, attestation_path = _paths(example)
    d = EXAMPLES / example
    return (
        spec,
        load_manifest(manifest_path),
        review_path,
        attestation_path,
        load_matrix(d / "traceability_matrix.a.json"),
        load_citations(d / "literal_citations.yaml"),
    )


def _build(example):
    spec, manifest, review_path, _, matrix, citations = _data(example)
    return build_attestation(spec, manifest, review_path.name, matrix, citations)


# ------------------------------------------------- drift pin + invariants

@pytest.mark.parametrize("example", sorted(COMMITTED))
def test_committed_attestation_drift_pin_and_invariants(example):
    """The drift-pin transition (v2 spec section 7): while an artifact is
    UNSIGNED, it must byte-match the generator; once signed, the byte pin
    deliberately no longer applies (a signature IS a divergence from the
    template) and the artifact is guarded instead by the structural
    invariants, which hold in both states."""
    spec, manifest_path, review_path, attestation_path = _paths(example)
    d = EXAMPLES / example
    report = check_example(
        attestation_path, manifest_path, review_path, d / "traceability_matrix.a.json"
    )
    if not report["attestation_complete"]:
        # unsigned: full byte-equality drift pin against the generator
        assert attestation_path.read_text(encoding="utf-8") == _build(example), example
    # signed or unsigned: structural invariants always hold
    assert report["structure_ok"] is True, (example, report)
    assert report["hash_current"] is True
    assert report["missing_fields"] == []
    assert report["missing_blocks"] == []
    assert report["missing_content"] == []


def test_all_committed_artifacts_are_currently_pending():
    """Committed state at build time: all four artifacts are PENDING (no
    signature exists yet). This test documents the expected repo state and
    will legitimately need dropping per-example as Steven signs - unlike the
    drift test above, which is designed to survive signatures."""
    for example in sorted(COMMITTED):
        spec, manifest_path, review_path, attestation_path = _paths(example)
        d = EXAMPLES / example
        report = check_example(
            attestation_path, manifest_path, review_path, d / "traceability_matrix.a.json"
        )
        assert report["attestation_complete"] is False, example


# ------------------------------------------------------ completion semantics

def test_completion_requires_the_folded_in_review_to_be_complete():
    """Replacing every _PENDING_ in the attestation (Wrong-if, Gap-if,
    Adopted, sign-off) is NOT enough while the Component D review is itself
    still pending - the two halves of the human act are mechanically linked.
    With both complete, attestation_complete flips true and the structural
    invariants still hold (the simulated post-signature state the drift-pin
    transition is designed for)."""
    spec, manifest, review_path, _, matrix, citations = _data("dosage_calculator")
    filled = build_attestation(spec, manifest, review_path.name, matrix, citations).replace(
        PENDING, "S. Dark / 2026-07-21 / eliminated: none sustained"
    )
    pending_review = review_path.read_text(encoding="utf-8")
    r1 = check_attestation(filled, manifest, pending_review, matrix=matrix)
    assert r1["structure_ok"] is True
    assert r1["review_complete"] is False
    assert r1["attestation_complete"] is False  # blocked on the D review
    completed_review = pending_review.replace(PENDING, "done")
    r2 = check_attestation(filled, manifest, completed_review, matrix=matrix)
    assert r2["review_complete"] is True
    assert r2["attestation_complete"] is True
    assert r2["structure_ok"] is True  # post-signature invariants hold
    assert r2["hash_current"] is True


# ------------------------------------------------------------- tamper cases

def test_contract_changed_after_signing_is_a_stale_attestation():
    """The tamper case the hash binding exists for: sign the artifact, then
    change the contract (weaken an ensures). The recorded hash no longer
    matches the current manifest, so the ratification reads stale - a signed
    adoption can never silently outlive the contract it adopted."""
    spec, manifest, review_path, _, matrix, citations = _data("dosage_calculator")
    signed = build_attestation(spec, manifest, review_path.name, matrix, citations).replace(
        PENDING, "S. Dark / 2026-07-21 / yes"
    )
    weakened_src = (EXAMPLES / "dosage_calculator" / "dosage.dfy").read_text(
        encoding="utf-8"
    ).replace("infusionRateMlPerHr > 0.0 || dose == 0.0",
              "infusionRateMlPerHr >= 0.0 || dose == 0.0")
    weakened_manifest = build_frozen_contract(spec, weakened_src)
    assert contract_hash(weakened_manifest) != contract_hash(manifest)
    review = review_path.read_text(encoding="utf-8").replace(PENDING, "done")
    report = check_attestation(signed, weakened_manifest, review, matrix=matrix)
    assert report["hash_current"] is False
    assert report["structure_ok"] is False  # stale, whatever else it says


def test_pasting_the_current_hash_elsewhere_cannot_mask_a_stale_recorded_hash():
    """Regression (Qodo, PR #75): hash_current must come from parsing the
    artifact's dedicated recorded-hash field and comparing equality - never
    an unanchored substring search. A stale recorded hash with the current
    hash pasted elsewhere in the document must still read stale."""
    spec, manifest, review_path, _, matrix, citations = _data("dosage_calculator")
    current = contract_hash(manifest)
    md = build_attestation(spec, manifest, review_path.name, matrix, citations)
    stale = "0" * 64
    spoofed = md.replace(current, stale) + f"\n\nnote: {current}\n"
    assert current in spoofed  # the spoof genuinely contains the current hash
    report = check_attestation(spoofed, manifest, review_path.read_text(encoding="utf-8"))
    assert report["recorded_hash"] == stale
    assert report["hash_current"] is False
    assert report["structure_ok"] is False


def test_gutted_declaration_content_is_caught_even_with_marker_intact():
    """Regression (Qodo, PR #75): keeping a declaration's heading marker
    while deleting the frozen content the human is supposed to be adopting
    must fail the structure gate - a heading alone is not a reviewable
    block."""
    spec, manifest, review_path, _, matrix, citations = _data("dosage_calculator")
    md = build_attestation(spec, manifest, review_path.name, matrix, citations)
    review = review_path.read_text(encoding="utf-8")
    # (a) delete ExpectedDose's fenced signature block, keep its heading
    sig = next(d for d in manifest["declarations"] if d["name"] == "ExpectedDose")["signature"]
    gutted = md.replace(sig, "")
    r1 = check_attestation(gutted, manifest, review, matrix=matrix)
    assert "ExpectedDose: signature" in r1["missing_content"]
    assert r1["structure_ok"] is False
    # (b) delete one ensures clause line from CalculateHourlyDose's section
    pinning = next(
        d for d in manifest["declarations"] if d["name"] == "CalculateHourlyDose"
    )["ensures"][0]
    gutted2 = md.replace(f"- ensures `{pinning}`\n", "")
    r2 = check_attestation(gutted2, manifest, review, matrix=matrix)
    assert "CalculateHourlyDose: ensures" in r2["missing_content"]
    assert r2["structure_ok"] is False


def test_gutted_production_fields_are_caught_per_section():
    """v2 tamper case: each declaration section must carry its OWN Wrong-if,
    Gap-if, and Adopted fields - another section's surviving copy must not
    mask a deletion."""
    spec, manifest, review_path, _, matrix, citations = _data("dosage_calculator")
    md = build_attestation(spec, manifest, review_path.name, matrix, citations)
    review = review_path.read_text(encoding="utf-8")
    for field, label in (("Wrong-if (rebutting)?", "Wrong-if"),
                         ("Gap-if (undercutting)?", "Gap-if"),
                         ("Adopted?", "Adopted")):
        line_start = f"**{field}** {PENDING}"
        assert md.count(line_start) == len(manifest["declarations"])
        gutted = md.replace(line_start, "**(field removed)**", 1)
        r = check_attestation(gutted, manifest, review, matrix=matrix)
        assert f"ExpectedDose: {label} field" in r["missing_content"]
        assert r["structure_ok"] is False


def test_gutted_requirement_text_is_caught():
    """v2 tamper case: deleting a mapped requirement's verbatim text from a
    declaration's section fails the gate - and the same mechanism makes a
    REQUIREMENT-TEXT CHANGE flag the artifact stale even though the contract
    hash (which binds only the contract surface) still matches: a
    ratification adopts a clause<->requirement correspondence."""
    spec, manifest, review_path, _, matrix, citations = _data("renal_adjustment")
    md = build_attestation(spec, manifest, review_path.name, matrix, citations)
    review = review_path.read_text(encoding="utf-8")
    gstage = next(d for d in manifest["declarations"] if d["name"] == "GStage")
    row = _matched_rows(gstage, matrix, spec)[0]
    assert row["requirement_id"] == "REQ-RENAL-1"
    gutted = md.replace(row["requirement_text"], "(requirement text removed)")
    r = check_attestation(gutted, manifest, review, matrix=matrix)
    assert "GStage: requirement REQ-RENAL-1" in r["missing_content"]
    assert r["structure_ok"] is False


def test_altered_requirement_id_is_caught_even_with_text_intact():
    """Regression (Qodo, this PR): the checker requires the FULL rendered
    requirement line (ID + verbatim text paired), not the text alone -
    otherwise the **REQ-...** marker could be removed or swapped while the
    text survives, degrading the clause<->requirement binding unnoticed."""
    spec, manifest, review_path, _, matrix, citations = _data("renal_adjustment")
    md = build_attestation(spec, manifest, review_path.name, matrix, citations)
    review = review_path.read_text(encoding="utf-8")
    tampered = md.replace("> **REQ-RENAL-1** —", "> **REQ-RENAL-999** —", 1)
    assert tampered != md
    r = check_attestation(tampered, manifest, review, matrix=matrix)
    assert "GStage: requirement REQ-RENAL-1" in r["missing_content"]
    assert r["structure_ok"] is False


def test_deleted_definitional_banner_is_caught():
    """Regression (Qodo, this PR): the definitional-proof banner is a safety
    signal directing reviewer doubt where mechanical evidence is weakest;
    deleting it from a declaration's section must fail the gate. Uses renal's
    GStage, definitional in the committed matrix."""
    from evidence.contract_attestation import _DEFINITIONAL_BANNER

    spec, manifest, review_path, _, matrix, citations = _data("renal_adjustment")
    md = build_attestation(spec, manifest, review_path.name, matrix, citations)
    review = review_path.read_text(encoding="utf-8")
    # remove the first banner occurrence - GStage's, the first definitional decl
    gutted = md.replace(_DEFINITIONAL_BANNER + "\n\n", "", 1)
    assert gutted != md
    r = check_attestation(gutted, manifest, review, matrix=matrix)
    assert "GStage: definitional banner" in r["missing_content"]
    assert r["structure_ok"] is False


# ------------------------------------- auto-assembly (the verified corrections)

def test_dosage_kernel_is_mapped_via_evidence_level_code_location():
    """The correction to the v2 design spec's row-only matching rule,
    verified against the real committed matrix: dosage's ROW code_location
    names the Python implementation (dosage.py::calculate_hourly_dose), so
    only evidence-level matching links CalculateHourlyDose to its two
    requirements - row-only matching would falsely mark the safety-critical
    kernel unmapped. ExpectedDose (a helper) is genuinely unmapped."""
    spec, manifest, _, _, matrix, _ = _data("dosage_calculator")
    calc = next(d for d in manifest["declarations"] if d["name"] == "CalculateHourlyDose")
    ids = [r["requirement_id"] for r in _matched_rows(calc, matrix, spec)]
    assert ids == ["REQ-GIP-1-4-12", "REQ-GIP-1-8-1"]
    helper = next(d for d in manifest["declarations"] if d["name"] == "ExpectedDose")
    assert _matched_rows(helper, matrix, spec) == []


def test_renal_evidence_only_functions_are_mapped():
    """Same correction, renal side: AssessRenalFunction appears at evidence
    level only (its rows' top-level code_location names other functions) and
    must still map."""
    spec, manifest, _, _, matrix, _ = _data("renal_adjustment")
    arf = next(d for d in manifest["declarations"] if d["name"] == "AssessRenalFunction")
    assert len(_matched_rows(arf, matrix, spec)) >= 1


def test_definitional_banner_targets_the_declaration_not_the_row():
    """The precision correction to the v2 design spec's any-evidence-in-row
    rule, verified against the real committed matrix: renal rows mix
    proof_content across declarations (REQ-RENAL-1 carries definitional
    GStage alongside property AssessRenalFunction), so the banner must key
    on the declaration's OWN evidence entry."""
    spec, manifest, _, _, matrix, _ = _data("renal_adjustment")
    by_name = {d["name"]: d for d in manifest["declarations"]}
    assert _is_definitional(by_name["GStage"], matrix, spec) is True
    # shares REQ-RENAL-1's row with GStage, but its own proof is property:
    assert _is_definitional(by_name["AssessRenalFunction"], matrix, spec) is False
    assert _is_definitional(by_name["RoundHalfUp"], matrix, spec) is False


def test_datatypes_render_the_honest_unmapped_line():
    """Type declarations have no matrix rows; their blocks carry the honest
    'none mapped' line (worded for type declarations, not implying a
    finding), and the reviewer confirms via Gap-if."""
    md = _build("drug_interaction_checker")
    assert md.count("none mapped in `traceability_matrix.a.json` (type declaration or helper/internal") == 6


def test_sourced_literals_render_with_quotes_and_dosage_has_none():
    """The sourced-literals block puts each declaration's source-cited
    constants next to their verbatim quotes; dosage (fully parameterized,
    structural zero only) correctly renders no such block."""
    renal = _build("renal_adjustment")
    assert '> `90` — kdigo-2024-gfr-staging.md: "G1 | ≥90 | Normal or high"' in renal
    dosage = _build("dosage_calculator")
    assert "Sourced literals in this declaration" not in dosage


# ------------------------------------------------------------- hash binding

def test_contract_hash_is_stable_and_content_sensitive():
    """Same manifest -> same hash; any contract-surface change -> different
    hash. The binding is over content, not formatting or generation time."""
    _, manifest_path, _, _ = _paths("aeb_kernel")
    manifest = load_manifest(manifest_path)
    assert contract_hash(manifest) == contract_hash(load_manifest(manifest_path))
    mutated = {**manifest, "declarations": manifest["declarations"][:-1]}
    assert contract_hash(mutated) != contract_hash(manifest)
