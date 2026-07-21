"""Tier 3 authoring migration: tests for evidence/contract_attestation.py -
the contract-ratification artifact (the human half of Component F).

The module builds the ratification TEMPLATE and mechanically checks its
structure; it never performs the ratification (drafter != checker). These
tests pin: the four committed artifacts match the generator (no drift) and
are structurally valid but PENDING; simulated completion flips
attestation_complete only when the folded-in Component D review is itself
complete; and the two tamper cases are caught - a contract changed after
signing (stale hash) and a dropped declaration block."""

import pathlib

import pytest

from evidence.contract_attestation import (
    build_attestation,
    check_attestation,
    check_example,
    contract_hash,
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


@pytest.mark.parametrize("example", sorted(COMMITTED))
def test_committed_attestation_matches_generator_and_is_pending(example):
    """No drift between the committed artifact and the generator; structure
    passes; PENDING until the human ratifies (and the folded-in Component D
    review is complete)."""
    spec, manifest_path, review_path, attestation_path = _paths(example)
    manifest = load_manifest(manifest_path)
    assert attestation_path.read_text(encoding="utf-8") == build_attestation(
        spec, manifest, review_path.name
    )
    report = check_example(attestation_path, manifest_path, review_path)
    assert report["structure_ok"] is True, (example, report)
    assert report["hash_current"] is True
    assert report["missing_fields"] == []
    assert report["missing_blocks"] == []
    assert report["attestation_complete"] is False  # PENDING until ratified


def test_completion_requires_the_folded_in_review_to_be_complete():
    """Replacing every _PENDING_ in the attestation is NOT enough while the
    Component D review is itself still pending - the two halves of the human
    act are mechanically linked. With both complete, attestation_complete
    flips true."""
    spec, manifest_path, review_path, _ = _paths("dosage_calculator")
    manifest = load_manifest(manifest_path)
    filled = build_attestation(spec, manifest, review_path.name).replace(
        PENDING, "S. Dark / 2026-07-21 / yes"
    )
    pending_review = review_path.read_text(encoding="utf-8")
    r1 = check_attestation(filled, manifest, pending_review)
    assert r1["structure_ok"] is True
    assert r1["review_complete"] is False
    assert r1["attestation_complete"] is False  # blocked on the D review
    completed_review = pending_review.replace(PENDING, "done")
    r2 = check_attestation(filled, manifest, completed_review)
    assert r2["review_complete"] is True
    assert r2["attestation_complete"] is True


def test_contract_changed_after_signing_is_a_stale_attestation():
    """The tamper case the hash binding exists for: sign the artifact, then
    change the contract (weaken an ensures). The recorded hash no longer
    matches the current manifest, so the ratification reads stale - a signed
    adoption can never silently outlive the contract it adopted."""
    spec, manifest_path, review_path, _ = _paths("dosage_calculator")
    manifest = load_manifest(manifest_path)
    signed = build_attestation(spec, manifest, review_path.name).replace(
        PENDING, "S. Dark / 2026-07-21 / yes"
    )
    # the contract then changes: rebuild the manifest from a weakened spec
    weakened_src = (EXAMPLES / "dosage_calculator" / "dosage.dfy").read_text(
        encoding="utf-8"
    ).replace("infusionRateMlPerHr > 0.0 || dose == 0.0",
              "infusionRateMlPerHr >= 0.0 || dose == 0.0")
    weakened_manifest = build_frozen_contract(spec, weakened_src)
    assert contract_hash(weakened_manifest) != contract_hash(manifest)
    review = review_path.read_text(encoding="utf-8").replace(PENDING, "done")
    report = check_attestation(signed, weakened_manifest, review)
    assert report["hash_current"] is False
    assert report["structure_ok"] is False  # stale, whatever else it says


def test_dropped_declaration_block_is_caught():
    """Removing one declaration's block from the artifact (its unique marker)
    is a structural failure, even though every field keyword still appears in
    the other blocks."""
    spec, manifest_path, review_path, _ = _paths("dosage_calculator")
    manifest = load_manifest(manifest_path)
    md = build_attestation(spec, manifest, review_path.name)
    gutted = md.replace("### function `ExpectedDose`", "### (removed)")
    report = check_attestation(gutted, manifest, review_path.read_text(encoding="utf-8"))
    assert "ExpectedDose" in report["missing_blocks"]
    assert report["structure_ok"] is False


def test_pasting_the_current_hash_elsewhere_cannot_mask_a_stale_recorded_hash():
    """Regression (Qodo #1): hash_current must come from parsing the
    artifact's dedicated recorded-hash field and comparing equality - never
    an unanchored substring search. A stale recorded hash with the current
    hash pasted elsewhere in the document must still read stale."""
    spec, manifest_path, review_path, _ = _paths("dosage_calculator")
    manifest = load_manifest(manifest_path)
    current = contract_hash(manifest)
    md = build_attestation(spec, manifest, review_path.name)
    stale = "0" * 64
    spoofed = md.replace(current, stale) + f"\n\nnote: {current}\n"
    assert current in spoofed  # the spoof genuinely contains the current hash
    report = check_attestation(spoofed, manifest, review_path.read_text(encoding="utf-8"))
    assert report["recorded_hash"] == stale
    assert report["hash_current"] is False
    assert report["structure_ok"] is False


def test_gutted_declaration_content_is_caught_even_with_marker_intact():
    """Regression (Qodo #2): keeping a declaration's heading marker while
    deleting the frozen content the human is supposed to be adopting (its
    signature/definition/clauses, or its own Adopted field) must fail the
    structure gate - a heading alone is not a reviewable block."""
    spec, manifest_path, review_path, _ = _paths("dosage_calculator")
    manifest = load_manifest(manifest_path)
    md = build_attestation(spec, manifest, review_path.name)
    review = review_path.read_text(encoding="utf-8")
    # (a) delete ExpectedDose's fenced signature block, keep its heading
    sig = next(d for d in manifest["declarations"] if d["name"] == "ExpectedDose")["signature"]
    gutted = md.replace(sig, "")
    r1 = check_attestation(gutted, manifest, review)
    assert "ExpectedDose: signature" in r1["missing_content"]
    assert r1["structure_ok"] is False
    # (b) delete one ensures clause line from CalculateHourlyDose's section
    pinning = next(
        d for d in manifest["declarations"] if d["name"] == "CalculateHourlyDose"
    )["ensures"][0]
    gutted2 = md.replace(f"- ensures `{pinning}`\n", "")
    r2 = check_attestation(gutted2, manifest, review)
    assert "CalculateHourlyDose: ensures" in r2["missing_content"]
    assert r2["structure_ok"] is False
    # (c) delete the FIRST section's own Adopted line (the second section's
    # still exists, so a global "Adopted somewhere in the file" check would
    # pass - the per-section check must not)
    adopted_line = (
        f"**Adopted?** {PENDING} (yes / no + notes — does this declaration "
        "mean what the requirement means?)"
    )
    assert md.count(adopted_line) == len(manifest["declarations"])
    gutted3 = md.replace(adopted_line, "**(field removed)**", 1)
    r3 = check_attestation(gutted3, manifest, review)
    assert "ExpectedDose: Adopted field" in r3["missing_content"]
    assert r3["structure_ok"] is False


def test_contract_hash_is_stable_and_content_sensitive():
    """Same manifest -> same hash; any contract-surface change -> different
    hash. The binding is over content, not formatting or generation time."""
    spec, manifest_path, _, _ = _paths("aeb_kernel")
    manifest = load_manifest(manifest_path)
    assert contract_hash(manifest) == contract_hash(load_manifest(manifest_path))
    mutated = {**manifest, "declarations": manifest["declarations"][:-1]}
    assert contract_hash(mutated) != contract_hash(manifest)
