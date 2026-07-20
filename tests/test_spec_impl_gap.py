"""Unit tests for evidence/spec_impl_gap.py - Component A, the
spec/implementation-gap classifier (definitional vs property).

No Dafny invocation: the classifier is pure Python + Z3 (structural
analysis with a best-effort Z3 pin-uniqueness cross-check), so these run
fast. Synthetic specs exercise the core mechanics; assertions against the
four real committed specs pin the by-hand analysis the whole
"PROVEN != meaningful" thread rests on - aeb_kernel is definitional,
dosage/renal carry real property content - so a future change to the
classifier can't silently reclassify them."""

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pytest  # noqa: E402

from evidence.spec_impl_gap import (  # noqa: E402
    classify_declaration,
    classify_source,
)

EX = REPO_ROOT / "examples"


# --------------------------------------------------------------- synthetic

# A pure predicate whose ensures restates its body: the canonical
# definitional (tautology) shape.
DEFINITIONAL = """
function IsHot(tempC: real): bool
  ensures IsHot(tempC) <==> tempC >= 40.0
{ tempC >= 40.0 }
"""

# A method whose result is pinned to a companion AND bounded: one
# definitional clause, one genuine property clause (the bound is strictly
# weaker than the pin).
MIXED_METHOD = """
function Clamp(x: real, hi: real): real
  requires hi > 0.0
{ if x < 0.0 then 0.0 else if x > hi then hi else x }
method Compute(x: real, hi: real) returns (y: real)
  requires hi > 0.0
  ensures y == Clamp(x, hi)
  ensures 0.0 <= y <= hi
{ y := Clamp(x, hi); }
"""

# A guarded, match-per-constructor definitional function (the aeb shape).
GUARDED = """
datatype Kind = A | B
function Pick(k: Kind, s: real): bool
  ensures k == A ==> (Pick(k, s) <==> (0.0 < s < 10.0))
  ensures k == B ==> (Pick(k, s) <==> (0.0 < s < 5.0))
{ match k case A => 0.0 < s < 10.0 case B => 0.0 < s < 5.0 }
"""


def test_definitional_predicate_is_definitional_and_z3_confirms():
    d = classify_declaration(DEFINITIONAL, "IsHot")
    assert d["overall"] == "definitional"
    assert len(d["clauses"]) == 1
    assert d["clauses"][0]["classification"] == "definitional"
    assert d["clauses"][0]["z3_check"] == "confirmed"


def test_mixed_method_has_both_a_definitional_pin_and_a_property_bound():
    d = classify_declaration(MIXED_METHOD, "Compute")
    kinds = [c["classification"] for c in d["clauses"]]
    assert kinds.count("definitional") == 1  # y == Clamp(x, hi)
    assert kinds.count("property") == 1  # 0.0 <= y <= hi
    assert d["overall"] == "property"  # any property clause -> property row
    # the pin's RHS is a companion call Z3 can't translate; the bound can be
    pin = next(c for c in d["clauses"] if c["classification"] == "definitional")
    bound = next(c for c in d["clauses"] if c["classification"] == "property")
    assert pin["z3_check"].startswith("not_attempted")
    assert bound["z3_check"] == "confirmed"


def test_guarded_match_function_is_definitional_with_guards_recorded():
    d = classify_declaration(GUARDED, "Pick")
    assert d["overall"] == "definitional"
    assert all(c["classification"] == "definitional" for c in d["clauses"])
    # each clause's implication antecedent is stripped and recorded as a guard
    assert all(c["guards"] for c in d["clauses"])
    assert all(c["z3_check"] == "confirmed" for c in d["clauses"])


def test_unknown_declaration_is_refused():
    with pytest.raises(SystemExit, match="no method or function named"):
        classify_declaration(DEFINITIONAL, "NoSuchFunction")


# ------------------------------------------------------------- real specs

def _by_name(source):
    return {d["name"]: d for d in classify_source(source)}


def test_aeb_kernel_every_function_is_definitional():
    """Every aeb_kernel function restates its own body (ensures F <==> E,
    body E) - the motivating definitional case. All are fully Z3-translatable
    (pure real comparisons), so every clause is not just structurally but
    semantically confirmed to pin its result."""
    decls = _by_name((EX / "aeb_kernel" / "aeb_kernel.dfy").read_text())
    assert decls, "expected aeb_kernel declarations"
    for name, d in decls.items():
        assert d["overall"] == "definitional", name
        for c in d["clauses"]:
            assert c["classification"] == "definitional", (name, c["clause"])
            assert c["z3_check"] == "confirmed", (name, c["clause"])


def test_dosage_calculate_hourly_dose_is_property_with_a_definitional_pin():
    """dosage's CalculateHourlyDose pins dose == ExpectedDose(...) (definitional)
    but also bounds 0.0 <= dose <= max and infusionRate > 0 || dose == 0
    (property) - so the row carries real content. The bounds are Z3-confirmed
    to leave the result freedom; ExpectedDose has no postcondition at all."""
    decls = _by_name((EX / "dosage_calculator" / "dosage.dfy").read_text())
    assert decls["ExpectedDose"]["overall"] == "no_postcondition"

    chd = decls["CalculateHourlyDose"]
    assert chd["kind"] == "method"
    assert chd["overall"] == "property"
    kinds = [c["classification"] for c in chd["clauses"]]
    assert kinds.count("definitional") == 1
    assert kinds.count("property") == 2
    for c in chd["clauses"]:
        if c["classification"] == "property":
            assert c["z3_check"] == "confirmed", c["clause"]


def test_renal_carries_both_property_and_definitional_functions():
    """renal_adjustment mixes real-arithmetic property functions (RoundHalfUp's
    rounding bound and >= 0 floor, ComposedCeiling's > 0.0) with definitional
    category-lookup functions (GStage) - the classifier separates them."""
    decls = _by_name((EX / "renal_adjustment" / "renal_adjustment.dfy").read_text())
    assert decls["RoundHalfUp"]["overall"] == "property"
    assert decls["ComposedCeiling"]["overall"] == "property"
    assert decls["GStage"]["overall"] == "definitional"
    # ComposedCeiling's > 0.0 bound is fully translatable and Z3-confirmed
    assert any(c["z3_check"] == "confirmed" for c in decls["ComposedCeiling"]["clauses"])


def test_ddi_check_interaction_is_definitional():
    """drug_interaction_checker's CheckInteraction is a per-case lookup: every
    ensures pins the result to an InteractionResult(...) constructor under a
    guard. Definitional (the parameterized-datatype RHS is not Z3-translatable,
    so this rests on structure, correctly refused rather than mis-modeled)."""
    decls = _by_name((EX / "drug_interaction_checker" / "drug_interaction_checker.dfy").read_text())
    ci = decls["CheckInteraction"]
    assert ci["overall"] == "definitional"
    assert all(c["classification"] == "definitional" for c in ci["clauses"])


def test_structure_and_z3_never_disagree_on_the_committed_specs():
    """The load-bearing correctness invariant: wherever the Z3 pin-uniqueness
    cross-check can run, it agrees with the structural verdict. A disagreement
    would mean the structural classifier is unsound on a real clause."""
    specs = [
        "aeb_kernel/aeb_kernel.dfy",
        "dosage_calculator/dosage.dfy",
        "renal_adjustment/renal_adjustment.dfy",
        "drug_interaction_checker/drug_interaction_checker.dfy",
    ]
    for rel in specs:
        for d in classify_source((EX / rel).read_text()):
            for c in d["clauses"]:
                assert not c["z3_check"].startswith("disagrees"), (rel, d["name"], c)
