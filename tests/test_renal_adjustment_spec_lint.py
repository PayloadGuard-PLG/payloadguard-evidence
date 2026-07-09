"""Phase D, Gate C3: applying the shared vectors 1-2 spec-lint machinery
(evidence/dafny_spec_lint.py) to the real, committed renal_adjustment.dfy
spec, mirroring tests/test_dafny_spec_lint.py's real-dosage-kernel tests.

Real gap found applying this (2026-07-09): AssessRenalFunction(formula:
Formula, renalFunctionValue: real) has a Formula-typed parameter its one
requires clause never mentions. check_precondition_satisfiability used to
build a Z3 symbol for every declared parameter regardless of use, so this
refused with "unsupported Dafny parameter type" even though the actual
precondition never touches formula. Fixed in dafny_spec_lint.py to only
model referenced parameters - see that module's docstring and
test_dafny_spec_lint.py's two new regression tests for the narrowed fix
itself. This file is the real-spec application that surfaced it.
"""

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.dafny_spec_lint import (  # noqa: E402
    check_precondition_satisfiability,
    scan_weak_postconditions,
)

SPEC = (REPO_ROOT / "examples" / "renal_adjustment" / "renal_adjustment.dfy").read_text()

ALL_FUNCTIONS = (
    "RoundHalfUp",
    "GStage",
    "SelectFormula",
    "ComposedCeiling",
    "AssessRenalFunction",
    "CockcroftGaultCrClMlPerMin",
    "AssessRenalFunctionFromInputs",
)


# ------------------------------------------------- vector 1: satisfiability

def test_every_function_precondition_is_satisfiable():
    """None of the seven functions' requires clauses are vacuous - a Dafny
    'clean pass' on renal_adjustment.dfy proves what it appears to prove,
    not something trivially true because no input could ever satisfy the
    precondition."""
    for name in ALL_FUNCTIONS:
        verdict, detail = check_precondition_satisfiability(SPEC, name)
        assert verdict == "sat", f"{name}: {detail}"


def test_assess_renal_function_no_longer_refused_for_its_unused_formula_param():
    """Named regression for the real gap this file's module docstring
    describes: AssessRenalFunction's Formula-typed parameter is never
    referenced by its requires clause, so the check must not refuse on it."""
    verdict, _ = check_precondition_satisfiability(SPEC, "AssessRenalFunction")
    assert verdict == "sat"


# --------------------------------------------- vector 2: weak postconditions

def test_weak_postcondition_warning_counts_match_the_real_spec():
    """Unlike dosage.dfy (which avoids one-way ==> entirely), five of the
    seven renal functions genuinely use ==> in their ensures clauses - this
    is expected here, not a regression: GStage/SelectFormula/AssessRenalFunction
    dispatch across exhaustive, mutually-exclusive branches, and every one
    of these clauses is independently STP-covered (Gate C4's ACCEPT/REJECT
    lemmas prove them pinning, not just satisfied) - a stronger, proof-based
    check than this heuristic lint provides on its own. Pinned exact counts
    so a future change to any ensures clause is caught, not silently
    absorbed."""
    expected_counts = {
        "RoundHalfUp": 0,
        "GStage": 6,
        "SelectFormula": 2,
        "ComposedCeiling": 0,
        "AssessRenalFunction": 4,
        "CockcroftGaultCrClMlPerMin": 2,
        "AssessRenalFunctionFromInputs": 2,
    }
    for name, expected in expected_counts.items():
        warnings = scan_weak_postconditions(SPEC, name)
        assert len(warnings) == expected, f"{name}: {warnings}"


def test_composed_ceiling_and_round_half_up_have_no_weak_postconditions():
    """The two functions whose ensures clauses use <=/== rather than ==>
    (ComposedCeiling's bounds, RoundHalfUp's interval) should stay clean -
    a true-negative check mirroring dosage.dfy's own pattern."""
    assert scan_weak_postconditions(SPEC, "RoundHalfUp") == []
    assert scan_weak_postconditions(SPEC, "ComposedCeiling") == []
