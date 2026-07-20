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

from evidence.frozen_contract import (
    build_frozen_contract,
    check_contract,
    check_example,
    load_manifest,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOSAGE = REPO_ROOT / "examples" / "dosage_calculator"
SPEC = DOSAGE / "dosage.dfy"
MANIFEST = DOSAGE / "frozen_contract.yaml"


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
