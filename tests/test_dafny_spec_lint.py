"""Phase C, Gate C3: vectors 1 and 2 (spec-text hardening).

Vector 1 (vacuous preconditions) and vector 2 (weak postconditions, best-
effort heuristic) both lint the Dafny SOURCE TEXT, not captured output -
see evidence/dafny_spec_lint.py's module docstring for the split with
evidence/dafny_adapter.py (vector 3, timeout/resource masking).
"""

import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.dafny_spec_lint import (  # noqa: E402
    check_precondition_satisfiability,
    extract_requires_clauses,
    scan_weak_postconditions,
)

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


# --------------------------------------------------------- vector 1: Z3

def test_real_dosage_kernel_precondition_is_satisfiable():
    """True-negative: the real, committed dosage.dfy spec's requires
    clauses are a genuine, non-vacuous precondition - the checker must not
    cry wolf on legitimate specs."""
    source = (ART_DIR / "dosage.dfy").read_text()
    verdict, detail = check_precondition_satisfiability(source, "CalculateHourlyDose")
    assert verdict == "sat", detail


def test_real_vacuous_precondition_fixture_is_unsat():
    """The load-bearing regression: examples/dosage_calculator/
    vacuous_precondition_probe.dfy is a REAL, committed Dafny file whose
    verifier run is a genuine clean pass (confirmed separately - Dafny
    reports 1 verified, 0 errors on it) precisely because its precondition
    (x > 0 && x < 0) can never hold. Z3 must catch what Dafny's own clean
    pass misses."""
    source = (ART_DIR / "vacuous_precondition_probe.dfy").read_text()
    verdict, detail = check_precondition_satisfiability(source, "VacuousExample")
    assert verdict == "unsat", detail


def test_requires_clause_extraction_matches_the_real_dosage_spec():
    source = (ART_DIR / "dosage.dfy").read_text()
    clauses = extract_requires_clauses(source, "CalculateHourlyDose")
    joined = " ".join(clauses)
    assert "concentrationMgPerMl > 0.0" in joined
    assert "maxSafeDoseMgPerHr > 0.0" in joined


def test_conjunction_of_satisfiable_clauses_is_satisfiable():
    source = """
    method Simple(x: int, y: int) returns (r: int)
      requires x > 0
      requires y > 0
      requires x + y < 1000
      ensures r == x + y
    {
      r := x + y;
    }
    """
    verdict, _ = check_precondition_satisfiability(source, "Simple")
    assert verdict == "sat"


def test_quantifier_in_precondition_is_refused_not_mistranslated():
    """Tier 1: an out-of-scope construct (forall) must raise, not be
    silently dropped or mistranslated into something satisfiable-looking."""
    source = """
    method Quant(x: int) returns (b: bool)
      requires forall y :: y > 0 ==> y != x
      ensures b == true
    {
      b := true;
    }
    """
    with pytest.raises(SystemExit, match="unsupported construct 'forall'"):
        check_precondition_satisfiability(source, "Quant")


def test_unknown_parameter_type_is_refused():
    source = """
    method Weird(a: array2<int>) returns (b: bool)
      requires a.Length0 > 0
      ensures b == true
    {
      b := true;
    }
    """
    with pytest.raises(SystemExit, match="unsupported Dafny parameter type"):
        check_precondition_satisfiability(source, "Weird")


def test_nat_parameter_gets_implicit_nonnegativity_constraint():
    """requires n < 0 on a nat parameter must be unsat - Dafny's own nat
    semantics (>= 0) are load-bearing for the satisfiability check, not
    something the checker can afford to ignore."""
    source = """
    method NatCheck(n: nat) returns (r: nat)
      requires n < 0
      ensures r == n
    {
      r := n;
    }
    """
    verdict, _ = check_precondition_satisfiability(source, "NatCheck")
    assert verdict == "unsat"


def test_method_with_no_requires_clause_is_trivially_satisfiable():
    source = """
    method NoReq(x: int) returns (r: int)
      ensures r == x
    {
      r := x;
    }
    """
    verdict, _ = check_precondition_satisfiability(source, "NoReq")
    assert verdict == "sat"


# ------------------------------------------------- vector 2: weak ensures

def test_real_dosage_kernel_has_no_weak_postcondition_warnings():
    """True-negative: the real dosage.dfy ensures clauses use <=/==/||,
    never ==>, so the heuristic must not flag anything on the live spec."""
    source = (ART_DIR / "dosage.dfy").read_text()
    warnings = scan_weak_postconditions(source, "CalculateHourlyDose")
    assert warnings == []


def test_one_way_implication_postcondition_is_flagged():
    """The exact failure pattern the roadmap names: a one-way implication
    lets a broken implementation (e.g. one that always returns garbage
    when the antecedent is false) still satisfy the spec."""
    source = """
    method Weak(valid: bool, r: int) returns (r2: int)
      requires valid == true || valid == false
      ensures valid ==> r2 == r
    {
      r2 := r;
    }
    """
    warnings = scan_weak_postconditions(source, "Weak")
    assert len(warnings) == 1
    assert "valid ==> r2 == r" in warnings[0]


def test_bi_implication_postcondition_is_not_flagged():
    """True-negative: a clause already using <==> is exactly what the
    heuristic is nudging authors toward - it must not also be flagged."""
    source = """
    method BiImp(valid: bool, r: int) returns (r2: int)
      ensures valid <==> r2 == r
    {
      r2 := r;
    }
    """
    assert scan_weak_postconditions(source, "BiImp") == []
