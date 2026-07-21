"""Component F (Tier 3): tests for evidence/frozen_contract.py - the
frozen-contract integrity gate.

The gate proves a candidate .dfy preserves a human-authored spec's contract
surface (signatures + requires + ensures + function bodies) exactly and
introduces no soundness-escape construct (assume / {:axiom} / {:extern}). It
is an integrity guarantee, not a correctness one.

The load-bearing tests are the four verified-outcome cases for dosage, each
paired with what Dafny itself says (from the committed capture), so the point
is mechanical: the checker catches what Dafny accepts.

  case 1  dosage.dfy (real spec)          Dafny verifies      -> INTACT
  case 2  dosage_underconstrained.dfy     Dafny verifies      -> VIOLATED
  case 3  dosage_assume_escape.dfy        Dafny verifies      -> VIOLATED (assume)
  case 4  dosage_scaffolded.dfy           Dafny verifies      -> INTACT
"""

import pathlib

import pytest

from evidence.frozen_contract import (
    build_frozen_contract,
    check_contract,
    check_example,
    load_manifest,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
EXAMPLES = REPO_ROOT / "examples"
DOSAGE = EXAMPLES / "dosage_calculator"
SPEC = DOSAGE / "dosage.dfy"
MANIFEST = DOSAGE / "frozen_contract.yaml"

# Every worked example now under the frozen-contract gate: (spec .dfy, manifest).
# dosage is function/method only; renal/aeb/ddi also carry datatypes (ddi has a
# parameterized constructor, InteractionResult) - all frozen.
COMMITTED = {
    "dosage_calculator": ("dosage.dfy", "frozen_contract.yaml"),
    "renal_adjustment": ("renal_adjustment.dfy", "frozen_contract.yaml"),
    "aeb_kernel": ("aeb_kernel.dfy", "frozen_contract.yaml"),
    "drug_interaction_checker": ("drug_interaction_checker.dfy", "frozen_contract.yaml"),
}


def _dafny_verified(capture_name):
    """True iff the committed Dafny capture reports a clean verification
    ('N verified, 0 errors') - i.e. Dafny accepted the file."""
    text = (DOSAGE / capture_name).read_text(encoding="utf-8")
    return "verified, 0 errors" in text


# ------------------------------------------------------------------ drift

def test_committed_frozen_contract_matches_the_generator():
    """No drift between the committed frozen_contract.yaml and what the
    generator extracts from the current dosage.dfy. If the spec's contract
    surface changes, this fails until the frozen manifest is regenerated -
    a deliberate, human-noticed act, since freezing is the whole point."""
    committed = load_manifest(MANIFEST)
    # the committed file carries a header comment; compare parsed content
    committed.pop("_header", None)
    assert committed == build_frozen_contract("dosage.dfy", SPEC.read_text(encoding="utf-8"))


# ------------------------------------------------- the four verified outcomes

def test_case1_real_spec_is_contract_intact():
    report = check_example(SPEC, MANIFEST)
    assert report["verdict"] == "CONTRACT_INTACT"
    assert report["violations"] == []
    assert _dafny_verified("raw_dafny_output.txt")  # Dafny verifies the real spec


def test_case2_underconstrained_is_violated_while_dafny_verifies_it():
    """The existing weakened-ensures specimen: Dafny verifies it (it proves
    almost nothing), the checker rejects it, naming the dropped pinning
    ensures and the vanished ExpectedDose."""
    assert _dafny_verified("raw_dafny_output_underconstrained.txt")
    report = check_example(DOSAGE / "dosage_underconstrained.dfy", MANIFEST)
    assert report["verdict"] == "CONTRACT_VIOLATED"
    assert "CalculateHourlyDose" in report["ensures_mismatches"]
    assert "ExpectedDose" in report["missing_declarations"]


def test_case3_assume_escape_is_violated_on_the_forbidden_assume():
    """Contract surface pristine, implementation wrong, `assume false` forces
    Dafny to accept it (verifier reports 0 errors). The contract-surface diff
    sees nothing; the forbidden-construct scan catches the assume."""
    assert _dafny_verified("raw_dafny_output_assume_escape.txt")
    report = check_example(DOSAGE / "dosage_assume_escape.dfy", MANIFEST)
    assert report["verdict"] == "CONTRACT_VIOLATED"
    # the contract surface itself is untouched - only the escape hatch differs
    assert report["ensures_mismatches"] == []
    assert report["signature_mismatches"] == []
    assert report["missing_declarations"] == []
    assert ("assume", "CalculateHourlyDose") in report["forbidden_constructs"]


def test_case4_legitimate_scaffolding_is_intact():
    """The true-negative control: same contract, correct implementation, plus
    a whitelisted `assert` in the (non-frozen) method body. Dafny verifies and
    the checker stays INTACT - the gate does not cry wolf on honest proof
    scaffolding."""
    assert _dafny_verified("raw_dafny_output_scaffolded.txt")
    report = check_example(DOSAGE / "dosage_scaffolded.dfy", MANIFEST)
    assert report["verdict"] == "CONTRACT_INTACT"
    assert report["violations"] == []


# ------------------------------------------------------------- unit checks

def test_canonicalization_ignores_formatting_but_catches_token_changes():
    """AST-grade: reformatting (whitespace, comments) is invisible; a real
    token change is not."""
    base = "function F(x: int): int requires x > 0 { x + 1 }"
    manifest = build_frozen_contract("f.dfy", base)
    # same contract, only reformatted + a comment added
    reformatted = "function F(x:int):int\n  requires x>0  // a note\n{ x  +  1 }"
    assert check_contract(reformatted, manifest)["verdict"] == "CONTRACT_INTACT"
    # a real change to the body (x + 1 -> x + 2) is caught
    changed = "function F(x: int): int requires x > 0 { x + 2 }"
    r = check_contract(changed, manifest)
    assert r["verdict"] == "CONTRACT_VIOLATED"
    assert "F" in r["body_mismatches"]
    # a weakened precondition (x > 0 -> x >= 0) is caught
    weakened = "function F(x: int): int requires x >= 0 { x + 1 }"
    assert "F" in check_contract(weakened, manifest)["requires_mismatches"]


def test_axiom_attribute_is_a_forbidden_construct():
    """`{:axiom}` (an unproven-axiom marker) is caught the same way `assume`
    is - a declaration asserted true without proof."""
    base = "function F(x: int): int requires x > 0 { x + 1 }"
    manifest = build_frozen_contract("f.dfy", base)
    axiomized = "function {:axiom} F(x: int): int requires x > 0 { x + 1 }"
    r = check_contract(axiomized, manifest)
    assert r["verdict"] == "CONTRACT_VIOLATED"
    assert any(c == "{:axiom}" for c, _ in r["forbidden_constructs"])


def test_added_lemma_is_allowed_but_added_function_is_not():
    """A new lemma is proof scaffolding and allowed; a new spec-bearing
    function that wasn't in the frozen contract is not."""
    base = "function F(x: int): int requires x > 0 { x + 1 }"
    manifest = build_frozen_contract("f.dfy", base)
    with_lemma = base + "\nlemma L() ensures 1 + 1 == 2 { }"
    assert check_contract(with_lemma, manifest)["verdict"] == "CONTRACT_INTACT"
    with_function = base + "\nfunction G(y: int): int { y }"
    r = check_contract(with_function, manifest)
    assert r["verdict"] == "CONTRACT_VIOLATED"
    assert "G" in r["added_spec_declarations"]


def test_lemma_bearing_source_builds_and_lemmas_are_not_frozen():
    """Regression (Qodo #1): a spec containing a lemma must not crash manifest
    generation. The lemma is proof scaffolding, so it is not frozen - only the
    function/method contract surface is."""
    src = "function F(x: int): int requires x > 0 { x + 1 }\nlemma L() ensures 1 + 1 == 2 { }"
    manifest = build_frozen_contract("f.dfy", src)  # must not raise
    assert [d["name"] for d in manifest["declarations"]] == ["F"]  # lemma not frozen
    assert check_contract(src, manifest)["verdict"] == "CONTRACT_INTACT"


def test_still_unmodeled_kinds_fail_closed():
    """A kind the gate doesn't model yet (e.g. `newtype`/`class`) must fail
    closed - build refuses it, and a candidate that adds one is a violation -
    rather than silently pass a construct it can't diff. (datatypes ARE modeled
    now; see the datatype tests below.)"""
    with pytest.raises(SystemExit):
        build_frozen_contract("n.dfy", "newtype Small = x: int | 0 <= x < 10\nfunction F(): int { 0 }")

    base = "function F(x: int): int requires x > 0 { x + 1 }"
    manifest = build_frozen_contract("f.dfy", base)
    r = check_contract(base + "\nclass C { }", manifest)
    assert r["verdict"] == "CONTRACT_VIOLATED"
    assert ("class", "C") in r["unmodeled_declarations"]


# --------------------------------------------------- datatype freezing (extension)

DDI = EXAMPLES / "drug_interaction_checker" / "drug_interaction_checker.dfy"


def _ddi_manifest():
    return build_frozen_contract("drug_interaction_checker.dfy", DDI.read_text(encoding="utf-8"))


def test_datatypes_are_frozen_including_parameterized_constructors():
    """The datatype definitions (the constructors ARE the spec's meaning) are
    part of the frozen surface - enums and the parameterized InteractionResult
    alike."""
    manifest = _ddi_manifest()
    frozen = {d["name"]: d for d in manifest["declarations"] if d["kind"] == "datatype"}
    assert "Outcome" in frozen and "InteractionResult" in frozen
    assert "outcome : Outcome , direction : RiskDirection" in frozen["InteractionResult"]["definition"]


def test_dropping_a_datatype_constructor_is_caught():
    """Silently narrowing a datatype (dropping a constructor) changes the spec
    and must be a violation - Dafny would happily re-verify a spec built on the
    narrower type."""
    manifest = _ddi_manifest()
    tampered = DDI.read_text(encoding="utf-8").replace(
        "| Contraindicated | DoseReductionAdvised | NotCovered",
        "| Contraindicated | NotCovered",
    )
    r = check_contract(tampered, manifest)
    assert r["verdict"] == "CONTRACT_VIOLATED"
    assert "Outcome" in r["definition_mismatches"]


def test_changing_a_parameterized_field_type_is_caught():
    """A field-type change inside a parameterized constructor
    (RiskDirection -> Outcome) is a real spec change and must be caught."""
    manifest = _ddi_manifest()
    tampered = DDI.read_text(encoding="utf-8").replace(
        "InteractionResult(outcome: Outcome, direction: RiskDirection)",
        "InteractionResult(outcome: Outcome, direction: Outcome)",
    )
    r = check_contract(tampered, manifest)
    assert r["verdict"] == "CONTRACT_VIOLATED"
    assert "InteractionResult" in r["definition_mismatches"]


def test_reformatting_a_datatype_stays_intact():
    """AST-grade: adding whitespace and a comment inside a datatype is not a
    spec change."""
    manifest = _ddi_manifest()
    reformatted = DDI.read_text(encoding="utf-8").replace(
        "datatype DOAC = Apixaban | Dabigatran | Edoxaban | Rivaroxaban",
        "datatype DOAC =\n    Apixaban   // the first\n  | Dabigatran | Edoxaban | Rivaroxaban",
    )
    assert check_contract(reformatted, manifest)["verdict"] == "CONTRACT_INTACT"


@pytest.mark.parametrize("example", sorted(COMMITTED))
def test_committed_frozen_contract_matches_generator_and_self_checks_intact(example):
    """For every worked example: no drift between the committed
    frozen_contract.yaml and the generator, and the real spec checks INTACT
    against its own frozen contract."""
    spec_name, manifest_name = COMMITTED[example]
    spec = EXAMPLES / example / spec_name
    manifest_path = EXAMPLES / example / manifest_name
    committed = load_manifest(manifest_path)
    generated = build_frozen_contract(spec_name, spec.read_text(encoding="utf-8"))
    assert committed == generated, example
    assert check_example(spec, manifest_path)["verdict"] == "CONTRACT_INTACT"


def test_build_refuses_a_source_that_already_contains_a_forbidden_construct():
    """Regression (Qodo #3): forbidden constructs are ALWAYS forbidden, and the
    frozen baseline is guaranteed clean because build refuses a source that
    already contains one - which is what makes 'any hit in a candidate is an
    introduced escape' true rather than a baseline-diff the manifest can't do."""
    with pytest.raises(SystemExit):
        build_frozen_contract("a.dfy", "method M() ensures true { assume false; }")
